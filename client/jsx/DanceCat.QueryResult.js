var Constants = require('../js/DanceCat.Constants');


var ErrorResult = React.createClass({
  propTypes: {
    message: React.PropTypes.string,
    error_ext: React.PropTypes.array
  },

  render: function () {
    if (this.props.error_ext == null) {
      return <p className="error">{this.props.message}</p>
    }
    else{
      return (
        <div className="error">
          <p className="error">{this.props.message}</p>
          {this.props.error_ext.map(function (message, i) {
            return <p key={i}>{message}</p>
          })}
        </div>
      )
    }
  }
});

var ResultInRows = React.createClass({
  propType: {
    data: React.PropTypes.object
  },

  render: function () {
    return (
      <div className="table-responsive result-table">
        <table className="table table-striped">
          <thead>
            <tr>
              {this.props.data.header.map(function (title) {
                return <th key={title}>{title}</th>;
              })}
            </tr>
          </thead>
          <tbody>
            {this.props.data.rows.map(function (row, i) {
              return (
                <tr key={i}>
                  {this.props.data.header.map(function (title) {
                    return <td key={title}>{row[title]}</td>
                  })}
                </tr>
              )
            }, this)}
          </tbody>
        </table>
      </div>
    )
  }
});

var QueryResult = React.createClass({
  getInitialState: function () {
    return {
      data: {},
      error: '',
      error_ext: null,
      status: 0,
      seq: 0
    };
  },

  _resultReceived: function (data) {
    if (data.seq > this.state.seq) {
      if (data.status == 0){
        this.setState({
          data: {
            header: data.header,
            rows: data.data
          },
          error: '',
          status: data.status,
          seq: data.seq
        })
      } else {
        this.setState({
          data: {},
          error: data.error,
          status: data.status,
          seq: data.seq,
          error_ext: data.error_ext
        });
      }
    }
  },

  render: function () {
    if (this.state.seq > 0) {
      let content = null;
      if (this.state.status == -1) {
        content = <ErrorResult message={this.state.error}
                               error_ext={this.state.error_ext} />
      } else if (this.state.status == 0) {
        content = <ResultInRows data={this.state.data} />
      }

      return (
        <div>
          <h5>Query's Result:</h5>
          <hr/>
          { content }
        </div>
      )
    } else {
      return null;
    }
  }
});

var qr = ReactDOM.render(
  <QueryResult/>,
  document.getElementById('dc-query-result')
);

socket.on(Constants.WS_QUERY_RECEIVE, function (data) {
  $runQueryBtn.removeClass('disabled');
  qr._resultReceived(data);
});