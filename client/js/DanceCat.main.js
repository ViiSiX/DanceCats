/***** Style Section *****/
require('../../node_modules/bootstrap/dist/js/bootstrap.min');
require('../../node_modules/bootstrap/dist/css/bootstrap.min.css');
require('../css/justified-nav.css');
require('../css/dance-cat.css');
require('../../node_modules/codemirror/lib/codemirror.css');

/***** Library Section *****/
var autosize = require('../../node_modules/autosize/dist/autosize.min');
var CodeMirror = require('../../node_modules/codemirror/lib/codemirror');
require('../../node_modules/codemirror/mode/sql/sql');

module.exports['$'] = $;
module.exports['AutoSize'] = autosize;
module.exports['CodeMirror'] = CodeMirror;

module.exports['delete_on_click'] = function delete_on_click(el, delete_url, delete_obj_id) {
  $.post(
    delete_url,
    {
      id: delete_obj_id
    },
    function(ret_data) {
      if (ret_data.deleted) {
        $(el).remove()
      } else {
        alert("Failed to delete!")
      }
    }
  )
};

function led_remove_status(led_el) {
  led_el.removeClass('led-off led-yellow led-blue led-red led-green')
}

module.exports['db_connect_test_on_click'] = function db_connect_test_onclick(test_url, connection, led_el) {
  led_remove_status(led_el);
  led_el.addClass('led-yellow');

  let connection_data = {};

  for (let i = 0; i < connection.length; i++) {
    connection_data[connection[i]['name']] = connection[i]['value']
  }

  $.post(
    test_url,
    connection_data,
    function (ret_data) {
      led_remove_status(led_el);

      if (ret_data.connected) {
        led_el.addClass('led-green');
      } else {
        led_el.addClass('led-red');
      }
    }
  );
};

module.exports['ws_connect'] = function (connect_url) {
  return io.connect(connect_url);
};
