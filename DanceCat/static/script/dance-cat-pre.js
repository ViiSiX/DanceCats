function delete_onclick(el, delete_url, delete_obj_id) {
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
}

function led_remove_status(led_el) {
  led_el.removeClass('led-off led-yellow led-blue led-red led-green')
}

function db_connect_test_onclick(test_url, connection, led_el) {
  led_remove_status(led_el);
  led_el.addClass('led-yellow');
  var connection_data = {};
  for (var i = 0; i < connection.length; i++) {
    connection_data[connection[i]['name']] = connection[i]['value']
  }
  $.post(
    test_url,
    connection_data,
    function(ret_data) {
      led_remove_status(led_el);
      if (ret_data.connected) {
        led_el.addClass('led-green');
      } else {
        led_el.addClass('led-red');
      }
    }
  )
}