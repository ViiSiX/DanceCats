"""
Docstring for DanceCats.JobWorker module.

This module contains the job's workers that will be
passed to the RQ worker to run in the background.
"""

from __future__ import print_function
import traceback
from flask_mail import Message
from StringIO import StringIO
from pyexcel.sheets import Sheet
from DanceCats.DatabaseConnector \
    import DatabaseConnector, DatabaseConnectorException
from .Helpers import Timer


def job_worker_send_mail_result(tracker_id, job_name, recipients):
    """Enqueue this function to sent results to recipients.

    :param tracker_id: Job tracker id of tracking object.
    :param job_name: Name of the Job.
    :param recipients: List of emails.
    :return: None.
    """

    print(
        "Begin sending results to recipients of job {job_name}, "
        "tracker {tracker_id}".format(
            job_name=job_name,
            tracker_id=tracker_id
        )
    )

    from DanceCats import app, rdb, mail

    with app.app_context():
        queue = rdb.queue['default']
        result = queue.fetch_job(str(tracker_id)).result

        results_file = StringIO()
        results_file_data = [list(result['header'])]

        for row in result['rows']:
            results_file_data.append(list(row))

        Sheet(results_file_data).save_to_memory("xlsx", results_file)

        message = Message(
            "Job {job_name} ran successfully on DanceCats!".format(
                job_name=job_name
            ),
            recipients=recipients,
            body="Dear users,\n\nPlease kindly notice that "
                 "the job \"{job_name}\" ran successfully.\n"
                 "We attached the result in this email "
                 "for your later check.\n\n"
                 "DanceCats.".format(job_name=job_name)
        )

        message.attach(
            "Result_tid_{tracker_id}.xlsx".format(tracker_id=tracker_id),
            content_type="application/"
                         "vnd.openxmlformats-officedocument."
                         "spreadsheetml.sheet",
            data=results_file.getvalue()
        )

        mail.send(message)


def job_worker_query(job_id, tracker_id):
    """Enqueue this function for querying database.

    For now only focus on execute and save results to redis.
    :param job_id: Id of job that will be run.
    :param tracker_id: Job tracker id of tracking object.
    :return: Query result.
    """
    timer = Timer()

    print(
        "Begin executing job {job_id} with tracker {tracker_id}".
        format(job_id=job_id, tracker_id=tracker_id)
    )

    from .Models import QueryDataJob, TrackJobRun
    from DanceCats import app, db, rdb, config, \
        Constants

    job = QueryDataJob.query.get(job_id)
    job.update_executed_times()

    tracker = TrackJobRun.query.get(tracker_id)
    tracker.start()
    db.session.commit()

    try:
        db_connector = DatabaseConnector(
            job.Connection.type,
            job.Connection.db_config_generator(),
            sql_data_style=False,
            dict_format=False,
            timeout=job[Constants.JOB_FEATURE_QUERY_TIME_OUT]
            if Constants.JOB_FEATURE_QUERY_TIME_OUT in job
            else config.get('DB_TIMEOUT', 0)
        )

        db_connector.connect()
        db_connector.execute(job.query_string)
        results = {
            'header': db_connector.columns_name,
            'rows': db_connector.fetch_all()
        }
        db_connector.close()

        tracker.complete(
            is_success=True,
            run_duration=timer.get_total_milliseconds()
        )
        db.session.commit()

        if len(job.emails) > 0:
            with app.app_context():
                queue = rdb.queue['mailer']
                queue.enqueue(
                    f=job_worker_send_mail_result,
                    kwargs={
                        'tracker_id': tracker_id,
                        'job_name': job.name,
                        'recipients': job.recipients
                    },
                    job_id='mail_{tracker_id}'.format(tracker_id=tracker_id)
                )

        return results

    except DatabaseConnectorException as exception:
        tracker.complete(
            is_success=False,
            run_duration=timer.get_total_milliseconds(),
            error_string='{0}\n{1}\n{2}'.format(
                exception.message,
                exception.trace_back,
                traceback.format_exc()
            )
        )
        db.session.commit()

    except Exception as exception:
        tracker.complete(
            is_success=False,
            run_duration=timer.get_total_milliseconds(),
            error_string=str(exception) + "\n" + traceback.format_exc()
        )
        db.session.commit()

    return None
