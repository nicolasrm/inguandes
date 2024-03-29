/*!
 * jQuery form validation plugin
 * Author: Juan Pablo Canepa (jpcanepa)
 * Version 0.1
 *
 * JQuery Bolierplate credit:
 * jQuery lightweight plugin boilerplate
 * Original author: @ajpiano
 * Further changes, comments: @addyosmani
 * Licensed under the MIT license
 */
;(function ( $, window, document, undefined ) {

        // Create the defaults once
        var pluginName = 'validator',
            /* Default options */
        defaults = {
            'errorMessageClass' : 'help-inline'
        },

        /* All validators */
        validators = {
            'non-empty' : function (element) { 
                return getElementValue(element).length > 0
            },
            'is-number' : function (element) {
                if(getElementValue(element).length > 0) {
                    try {
                        var intVal = parseInt(getElementValue(element), 10);
                        return true;
                    } catch (e) {
                        return false;
                    }
                }
                else {
                    return true;
                }
            },
            'non-negative' : function (element) {
                if(getElementValue(element).length > 0) {
                    try {
                        return parseInt(getElementValue(element), 10) >= 0; 
                    } catch (e) {
                        return false;
                    }
                }
                else {
                    return true;
                }
            },
            'positive' : function (element) {
                if(getElementValue(element).length > 0) {
                    try {
                        return parseInt(getElementValue(element), 10) > 0; 
                    } catch (e) {
                        return false;
                    }
                }
                else {
                    return true;
                }
            },
            'is-percentage' : function (element) {
                if(getElementValue(element).length > 0) {
                    try {
                        return parseInt(getElementValue(element), 10) >= 0 && parseInt(getElementValue(element), 10) <= 100; 
                    } catch (e) {
                        return false;
                    }
                }
                else {
                    return true;
                }
            }
        };

        // The actual plugin constructor
        function Plugin( element, options ) {
            this.element = element;
            this.options = $.extend( {}, defaults, options) ;
            /* Register custom validators */
            if(options !== undefined && typeof(options.validators) != 'undefined')
                $.extend( validators, options.validators); 
            this._defaults = defaults;
            this._name = pluginName;

            this.init();
        }

        /* Gets the value of an element */
        function getElementValue(element) {
            if(element.is('input') || element.is('textarea')) {
                return $.trim(element.val());
            }
        }

		/* Creates a validation handler */
        function createValidator(validatorType, element) {
            return function() {
                var validatorArray = validatorType.split(" "),
                    ready = true;
                
                $.each(validatorArray, function (index, validator) {
                        if(!validators[validator](element)) {                        
                            ready = false;
                            return false;
                        }
                });
                return ready;
            }
        }
        
        /* Start validation */
        function startValidation(that) {
            var validation = true;

            /* Run the validator for each element */
            that.fields.each(
                function (index, element) {
                    var e = $(element);
                    if(!element.doValidation()) {
                        validation = false;

                        /* Add the "error" class to the container group */
                        e.closest('div.control-group')
                        .addClass('error');
                        
                        /* Show the error message */
                        if(that._defaults.errorMessageClass) {
                            e.closest('div.control-group')
                            .find('.' + that._defaults.errorMessageClass)
                            .show();
                        }
                    }
                    else {
                        /* If validation passed, remove the error class */
                        e.closest('div.control-group')
                        .removeClass('error');
                        
                        /* Hide the error message */
                        if(that._defaults.errorMessageClass) {
                            e.closest('div.control-group')
                            .find('.' + that._defaults.errorMessageClass)
                            .hide();
                        }
                    }
                }
            );

            /* Stop the submit if validation failed */
            return validation;
        }

        Plugin.prototype = {

            init: function () {
                var that = this,
                    mainForm = $(this.element);

                /* Capture all the fields that must be validated */
                that.fields = mainForm.find('[data-validator]');

                /* Attach the validators to the fields */
                that.fields.each(function (index, element) {
                        var e = $(element);
                        element.doValidation = createValidator(e.attr('data-validator'), e);
                        
                        /* Hide error messages from inputs */                        
                        if(that._defaults.errorMessageClass) {                                                        
                            e.closest('div.control-group')
                            .find('.' + that._defaults.errorMessageClass)
                            .hide();
                        }
                });
                
                /* Handle the form submit action */
                mainForm.submit(function () {
                        return startValidation(that);
                });
            }, 
            
            doValidation: function (callback) {
                callback(startValidation(this));
            }
        };

        $.fn[pluginName] = function ( options ) {
            var args = arguments;
            if (options === undefined || typeof options === 'object') {
                return this.each(function () {
                        if (!$.data(this, 'plugin_' + pluginName)) {
                            $.data(this, 'plugin_' + pluginName, new Plugin( this, options ));
                        }
                });
            } else if (typeof options === 'string' && options[0] !== '_' && options !== 'init') {
                return this.each(function () {
                        var instance = $.data(this, 'plugin_' + pluginName);
                        if (instance instanceof Plugin && typeof instance[options] === 'function') {
                            instance[options].apply( instance, Array.prototype.slice.call( args, 1 ) );
                        }
                });
            }
        }

})( jQuery, window, document );
