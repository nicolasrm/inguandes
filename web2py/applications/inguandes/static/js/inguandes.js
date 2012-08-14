(function (window) {
    'use strict';
    var $ = window.jQuery,
            Modernizr = window.Modernizr,
            yepnope = window.yepnope,
            INGUANDES = window.INGUANDES,
            datepicker_options = {
                format: 'yyyy-mm-dd',
                weekStart: 1,
                language: 'es'
            };
            
    INGUANDES.notify = function (level, message) {
        var local_level = '',
            alert_row,
            alert_element;

        if (level === 'error' || level === 'success' || level === 'info' || level === 'warning') {
            local_level = 'alert-' + level;
        }

        if (message) {
            alert_row = $('[data-type=template-alert]').clone();
            alert_row.css({
                position: 'fixed',
                top: 45
            });
            alert_element = alert_row.find('.alert');
            if (local_level) {
                alert_element.addClass(local_level);
            }
            alert_element.addClass('fade in');
            alert_element.find('[data-type=alert-text]').html(message);
            $('div.container').append(alert_row);
            alert_row.fadeIn(200, function () {
                setTimeout(function () {
                    alert_element.alert('close');
                }, 5000);
            });
            alert_row.on('closed', function () {
                alert_row.remove();
            });
        }
    }
    
    INGUANDES.startDateFields = function (fn) {
        yepnope([{
            test: Modernizr.date,
            nope: {
                'datepicker': INGUANDES.static_js_url + '/bootstrap-datepicker.js',
                'datepicker-es': INGUANDES.static_js_url + '/bootstrap-datepicker.es.js',
                'datepicker-css': INGUANDES.static_css_url + '/bootstrap-datepicker.css'
            },
            callback: {
                'datepicker': function (url, result, key) {
                    var campos_fecha = $('input[type="date"]');
                    campos_fecha.each(function (index, campo) {
                        $(campo).replaceWith(function () {
                            var date_field = $(this).clone(true);
                            date_field.attr('type', 'text');
                            date_field.addClass('input-small');
                            date_field.datepicker(datepicker_options);
                            return date_field;
                        });
                    });
                    if (fn) {
                        fn();
                    }
                }
            }
        }]);
    }
    
    INGUANDES.startDatetimeFields = function () {
        var deafult_hour = '10:00:00';
        yepnope([{
            test: Modernizr.datetime,
            nope: {
                'datepicker':       INGUANDES.static_js_url + '/bootstrap-datepicker.js',
                'datepicker-es':    INGUANDES.static_js_url + '/bootstrap-datepicker.es.js',
                'datepicker-css':   INGUANDES.static_css_url + '/bootstrap-datepicker.css',
                'timepicker':       INGUANDES.static_js_url + '/bootstrap-timepicker.js',
                'timepicker-css':   INGUANDES.static_css_url + '/bootstrap-timepicker.css'
            },
            callback: {
                'timepicker': function (url, result, key) {
                    var datetime_fields = $('input[type="datetime"]');
                    datetime_fields.each(function (index, field) {
                        var original_value = $(field).val().split(' '),
                            original_hour_arr,
                            original_hour = '',
                            original_date = '',
                            aux_date,
                            future_date;
                        if (!original_value[0]) {
                            aux_date = new Date();
                            future_date = new Date(aux_date.getUTCFullYear(),
                                aux_date.getUTCMonth(),
                                aux_date.getUTCDate());
                            original_value[0] = future_date.toISOString().split('T')[0];
                            original_value[1] = deafult_hour;
                        }

                        original_date = original_value[0];
                        original_hour_arr = original_value[1].split(':');
                        if (original_hour_arr[0] >= 12) {
                            original_hour = String(original_hour_arr[0] - 12);
                            if (original_hour.length === 1) {
                                original_hour = '0' + original_hour;
                            }
                            original_hour = original_hour + ':' + original_hour_arr[1] + ' PM';
                        } else {
                            original_hour = original_hour_arr[0] + ':' + original_hour_arr[1] + ' AM';
                        }

                        $(field).replaceWith(function () {
                            var datetime_field = $(this),
                                container = $('<div></div>'),
                                date_field = $('<input class="input-small" type="text" />'),
                                hour_field = $('<input class="input-mini" type="text" />'),
                                hidden_field = $('<input type="hidden" />');

                            hidden_field.val(original_value[0] + ' ' + original_value[1]);
                            hidden_field.attr('name', datetime_field.attr('name'));
                            hidden_field.attr('id', datetime_field.attr('id'));

                            date_field.attr('id', datetime_field.attr('id') + '_fecha');
                            date_field.attr('name', datetime_field.attr('name') + '_fecha');
                            date_field.attr('data-eliminar', 'true');
                            date_field.css('border-radius', '3px 0 0 3px');
                            date_field.addClass('input-mini');
                            date_field.on('change', function () {
                                var vals = hidden_field.val().split(' '),
                                    new_value = date_field.val() + ' ' + vals[1];
                                hidden_field.val(new_value);
                            });

                            hour_field.attr('id', datetime_field.attr('id') + '_hora');
                            hour_field.attr('name', datetime_field.attr('name') + '_hora');
                            hour_field.attr('data-eliminar', 'true');
                            hour_field.css('border-radius', '0 3px 3px 0');
                            hour_field.on('change', function () {
                                var vals = hidden_field.val().split(' '),
                                    date = vals[0],
                                    field_str = hour_field.val().split(' '),
                                    hourminute_str,
                                    hour,
                                    minute;

                                hourminute_str = field_str[0].split(':');
                                hour = parseInt(hourminute_str[0], 10);
                                minute = parseInt(hourminute_str[1], 10);
                                if (field_str[1] === 'PM') {
                                    hour = (hour + 12) % 24;
                                }

                                hour = hour > 10 ? hour : '0' + hour;
                                minute = minute > 10 ? minute : '0' + minute;

                                hidden_field.val(date + ' ' + hour + ':' + minute + ':00');
                            });

                            date_field.datepicker(datepicker_options);
                            hour_field.timepicker({
                                template: 'dropdown',
                                minuteStep: 30,
                                defaultTime: original_hour
                            });
                            date_field.val(original_date);
                            hour_field.val(original_hour);

                            container.append(date_field);
                            container.append(hour_field);
                            container.append(hidden_field);

                            return container;
                        });
                    });
                }
            }
        }]);
    };
    
    $(document).ready(function () {
        
    });
}(this));