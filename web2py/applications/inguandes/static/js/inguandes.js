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
                            var campo_fecha = $(this).clone(true);
                            campo_fecha.attr('type', 'text');
                            campo_fecha.datepicker(datepicker_options);
                            return campo_fecha;
                        });
                    });
                    if (fn) {
                        fn();
                    }
                }
            }
        }]);
    }
    
    $(document).ready(function () {
        
    });
}(this));