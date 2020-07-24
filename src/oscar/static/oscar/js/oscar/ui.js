/*global jQuery */

var oscar = (function(o, $) {
    // Replicate Django's flash messages so they can be used by AJAX callbacks.
    o.messages = {
        addMessage: function(tag, msg) {
            var msgHTML = '<div class="alert fade in alert-' + tag + '">' +
                '<a href="#" class="close" data-dismiss="alert">&times;</a>'  + msg +
                '</div>';
            $('#messages').append($(msgHTML));
        },
        debug: function(msg) { o.messages.addMessage('debug', msg); },
        info: function(msg) { o.messages.addMessage('info', msg); },
        success: function(msg) { o.messages.addMessage('success', msg); },
        warning: function(msg) { o.messages.addMessage('warning', msg); },
        error: function(msg) { o.messages.addMessage('danger', msg); },
        clear: function() {
            $('#messages').html('');
        },
        scrollTo: function() {
            $('html').animate({scrollTop: $('#messages').offset().top});
        }
    };

    o.search = {
        init: function() {
            o.search.initSortWidget();
            o.search.initFacetWidgets();
        },
        initSortWidget: function() {
            // Auto-submit (hidden) search form when selecting a new sort-by option
            $('#id_sort_by').on('change', function() {
                $(this).closest('form').submit();
            });
        },
        initFacetWidgets: function() {
            // Bind events to facet checkboxes
            $('.facet_checkbox').on('change', function() {
                window.location.href = $(this).nextAll('.facet_url').val();
            });
        }
    };

    // Notifications inbox within 'my account' section.
    o.notifications = {
        init: function() {
            $('a[data-behaviours~="archive"]').click(function() {
                o.notifications.checkAndSubmit($(this), 'archive');
            });
            $('a[data-behaviours~="delete"]').click(function() {
                o.notifications.checkAndSubmit($(this), 'delete');
            });
        },
        checkAndSubmit: function($ele, btn_val) {
            $ele.closest('tr').find('input').attr('checked', 'checked');
            $ele.closest('form').find('button[value="' + btn_val + '"]').click();
            return false;
        }
    };

    o.getCsrfToken = function() {
        // Extract CSRF token from cookies
        var cookies = document.cookie.split(';');
        var csrf_token = null;
        $.each(cookies, function(index, cookie) {
            var cookieParts = $.trim(cookie).split('=');
            if (cookieParts[0] == 'csrftoken') {
                csrf_token = cookieParts[1];
            }
        });
        // Extract from cookies fails for HTML-Only cookies
        if (! csrf_token) {
            csrf_token = $(document.forms.valueOf()).find('[name="csrfmiddlewaretoken"]')[0].value;
        }
        return csrf_token;
    };

    // Trigger adding new question when boxes are checked
    o.catalogue = {
        init: function(options) {
		if (typeof options == 'undefined') {
			options = {'catalogueURL': document.URL};
		}
		o.catalogue.url = options.catalogueURL || document.URL;
		o.catalogue.pk = options.composite || document.URL;
		$('.checked_ques').click(function() {
			if(this.checked) {
		        console.log($(this).val());
				var obj = {}
				obj['action'] = "add"
				obj['pk'] = $(this).val()
				obj['quiz_pk'] = o.catalogue.pk
		                var csrf = o.getCsrfToken();
                		    $.ajax({
		                        type: 'POST',
                		        data: JSON.stringify(obj),
		                        dataType: "json",
                		        contentType : 'application/json',
		                        url: o.catalogue.url,
                		        beforeSend: function(xhr) {
		                            xhr.setRequestHeader("X-CSRFToken", csrf);
                		        },
		                        success: function (data) {
	        	     		        // console.log(data, 'SUCCESS');
		        	                // location.reload();
                                    var text = $('.totalQues').text()
                                    console.log(text)
                                    var number = parseInt(text, 10) + 1
                                    console.log(number)
                                    document.getElementById("totalQuesNum").textContent = number
		                        },
                        		error: function (data) {
		                            console.log('ERROR', data);
                		        }
		                    });
			}
			else {
				var obj = {}
				obj['action'] = "remove"
				obj['pk'] = $(this).val()
				obj['quiz_pk'] = o.catalogue.pk
		                var csrf = o.getCsrfToken();
                		    $.ajax({
		                        type: 'POST',
					// data: JSON.stringify($(this).val()),
                		        data: JSON.stringify(obj),
		                        dataType: "json",
                		        contentType : 'application/json',
		                        url: o.catalogue.url,
                		        beforeSend: function(xhr) {
		                            xhr.setRequestHeader("X-CSRFToken", csrf);
                		        },
		                        success: function (data) {
	        	     		        // console.log(data, 'SUCCESS');
		        	                // location.reload();
                                    var text = $('.totalQues').text()
                                    // console.log(text)
                                    var number = parseInt(text, 10) - 1
                                    // console.log(number)
                                    document.getElementById("totalQuesNum").textContent = number
		                        },
                        		error: function (data) {
		                            console.log('ERROR', data);
                		        }
		                    });
			}
		});
	}
    };

    o.layout = {
        init: function(options) {
            if (typeof options == 'undefined') {
                options = {'layoutURL': document.URL};
            }
            o.layout.url = options.layoutURL || document.URL;
            o.layout.pk = options.template || document.URL;
            $('#update_template').click(function() {
                console.log(o.layout.url)
                console.log(o.layout.pk)
                var obj = {}
                obj['pk'] = o.layout.pk
                obj['tl'] = document.getElementById('side_tlheader').value
                obj['tr'] = document.getElementById('side_trheader').value
                obj['title'] = document.getElementById('side_title').value
                obj['bl'] = document.getElementById('side_blheader').value
                obj['br'] = document.getElementById('side_brheader').value
                obj['pn'] = document.getElementById('side_pn').value
                var csrf = o.getCsrfToken();
                    $.ajax({
                        type: 'POST',
                        data: JSON.stringify(obj),
                        dataType: "json",
                        contentType : 'application/json',
                        url: o.layout.url,
                        beforeSend: function(xhr) {
                            xhr.setRequestHeader("X-CSRFToken", csrf);
                        },
                        success: function (data) {
                             console.log(data, 'SUCCESS');
                            // location.reload();
                            document.getElementById("tlheader").textContent = document.getElementById('side_tlheader').value
                            document.getElementById("trheader").textContent = document.getElementById('side_trheader').value
                            document.getElementById("title").textContent = document.getElementById('side_title').value
                            document.getElementById("blheader").textContent = document.getElementById('side_blheader').value
                            document.getElementById("brheader").textContent = document.getElementById('side_brheader').value
                        },
                        error: function (data) {
                            console.log('ERROR', data);
                        }
                    });
            });
    }
    };

    o.select = {
        init: function(options) {
            if (typeof options == 'undefined') {
                options = {'createURL': document.URL};
            }
            o.select.url = options.createURL || document.URL;
            
            $('#next_step').click(function() {
                // Construct a list of filter
                var ques_type = [];
                var ques_topic = [];
                // Get all the checked boxes in the side_categories div
                $('.child_quiztype').each(function() {
                    // var key = $(this).closest('.card').find('.card-header')[0].innerText
                    // console.log(key)
                    // console.log($(this).val())
                    // if( key.trim() in ques_type) {
                    if ($(this)[0].checked) {
                        ques_type.push($(this).val().trim())
                    }
                    // }
                });

                // Get all the checked boxes in the side_categories div
                $('.quiztopic').each(function() {
                    if ($(this)[0].checked) {
                        ques_topic.push($(this).val().trim())
                    }
                });
                // console.log(ques_topic)
                // console.log(ques_type)
                var cat = $('#domain_selection').val()

                // Query data from the backend
                const q_type = new URLSearchParams({ques_type})
                const q_topic = new URLSearchParams({ques_topic})
                var temp_url = o.select.url + "?cat="+ cat + "&" + q_type.toString() + "&" + q_topic.toString();
                // var target_url = temp_url.concat(obj.toString());
                console.log(temp_url)
                window.location.href = temp_url;
            });
        }
    };

    o.create = {
        init: function(options) {
            if (typeof options == 'undefined') {
                options = {'layoutURL': document.URL};
            }
            o.create.next_url = options.layoutURL || document.URL;
            o.create.pk = options.composite || document.URL;
            
            $('#next_step').click(function() {
                var temp_url = o.create.next_url + "?pk="+ o.create.pk;
                window.location.href = temp_url;
            });
        }
    };

    o.template = {
        init: function(options) {
            if (typeof options == 'undefined') {
                options = {'detailURL': document.URL};
            }
            o.template.next_url = options.detailURL || document.URL;
            o.template.pk = options.composite || document.URL;

            $('#next_step').click(function() {
                var temp_url = o.template.next_url + "?pk="+ o.template.pk;
                window.location.href = temp_url;
            });
        }
    };

    // Site-wide forms events
    o.forms = {
        init: function() {
            // Forms with this behaviour are 'locked' once they are submitted to
            // prevent multiple submissions
            $('form[data-behaviours~="lock"]').submit(o.forms.submitIfNotLocked);

            // Disable buttons when they are clicked and show a "loading" message taken from the
            // data-loading-text attribute (http://getbootstrap.com/2.3.2/javascript.html#buttons).
            // Do not disable if button is inside a form with invalid fields.
            // This uses a delegated event so that it keeps working for forms that are reloaded
            // via AJAX: https://api.jquery.com/on/#direct-and-delegated-events
            $(document.body).on('submit', 'form', function(){
                var form = $(this);
                if ($(":invalid", form).length == 0)
                    $(this).find('button[data-loading-text]').button('loading');
            });
            // stuff for star rating on review page
            // show clickable stars instead of a select dropdown for product rating
            var ratings = $('.reviewrating');
            if(ratings.length){
                ratings.find('.star-rating i').on('click',o.forms.reviewRatingClick);
            }
        },
        submitIfNotLocked: function() {
            var $form = $(this);
            if ($form.data('locked')) {
                return false;
            }
            $form.data('locked', true);
        },
        reviewRatingClick: function(){
            var ratings = ['One','Two','Three','Four','Five']; //possible classes for display state
            $(this).parent().removeClass('One Two Three Four Five').addClass(ratings[$(this).index()]);
            $(this).closest('.controls').find('select').val($(this).index() + 1); //select is hidden, set value
        }
    };


    o.page = {
        init: function() {
            // Scroll to sections
            $('.top_page a').click(function(e) {
                var href = $(this).attr('href');
                $('html, body').animate({
                    scrollTop: $(href).offset().top
                }, 500);
                e.preventDefault();
            });
            // Tooltips
            $('[rel="tooltip"]').tooltip();
        }
    };

    o.responsive = {
        init: function() {
            if (o.responsive.isDesktop()) {
                o.responsive.initNav();
            }
        },
        isDesktop: function() {
            return document.body.clientWidth > 767;
        },
        initNav: function() {
            // Initial navigation for desktop
            var $sidebar = $('aside.col-sm-3'),
                $browse = $('[data-navigation="dropdown-menu"]'),
                $browseOpen = $browse.parent().find('> a[data-toggle]');
            // Set width of nav dropdown to be same as sidebar
            $browse.css('width', $sidebar.outerWidth());
            // Remove click on browse button if menu is currently open
            if (!$browseOpen.length) {
                $browse.parent().find('> a').off('click');
                // Set margin top of aside allow space for open navigation
                $sidebar.css({ marginTop: $browse.outerHeight() });
            }
        },
        initSlider: function() {
            $('.carousel').carousel({
                interval: 20000
            });
        }
    };

    // IE compabibility hacks
    o.compatibility = {
        init: function() {
            if (!o.compatibility.isIE()) return;
            // Set the width of a select in an overflow hidden container.
            // This is for add-to-basket forms within browing pages
            $('.product_pod select').on({
                mousedown: function(){
                    $(this).addClass("select-open");
                },
                change: function(){
                    $(this).removeClass("select-open");
                }
            });
        },
        isIE: function() {
            return navigator.userAgent.toLowerCase().indexOf("msie") > -1;
        }
    };

    o.basket = {
        is_form_being_submitted: false,
        init: function(options) {
            if (typeof options == 'undefined') {
                options = {'basketURL': document.URL};
            }
            o.basket.url = options.basketURL || document.URL;
            $('#content_inner').on('click', '#basket_formset a[data-behaviours~="remove"]', function(event) {
                o.basket.checkAndSubmit($(this), 'form', 'DELETE');
                event.preventDefault();
            });
            $('#content_inner').on('click', '#basket_formset a[data-behaviours~="save"]', function(event) {
                o.basket.checkAndSubmit($(this), 'form', 'save_for_later');
                event.preventDefault();
            });
            $('#content_inner').on('click', '#saved_basket_formset a[data-behaviours~="move"]', function() {
                o.basket.checkAndSubmit($(this), 'saved', 'move_to_basket');
            });
            $('#content_inner').on('click', '#saved_basket_formset a[data-behaviours~="remove"]', function(event) {
                o.basket.checkAndSubmit($(this), 'saved', 'DELETE');
                event.preventDefault();
            });
            $('#content_inner').on('click', '#voucher_form_link a', function(event) {
                o.basket.showVoucherForm();
                event.preventDefault();
            });
            $('#content_inner').on('click', '#voucher_form_cancel', function(event) {
                o.basket.hideVoucherForm();
                event.preventDefault();
            });
            $('#content_inner').on('submit', '#basket_formset', o.basket.submitBasketForm);
            if (window.location.hash == '#voucher') {
                o.basket.showVoucherForm();
            }
        },
        submitBasketForm: function(event) {
            $('#messages').html('');
            var payload = $('#basket_formset').serializeArray();
            $.post(o.basket.url, payload, o.basket.submitFormSuccess, 'json');
            if (event) {
                event.preventDefault();
            }
        },
        submitFormSuccess: function(data) {
            $('#content_inner').html(data.content_html);

            // Show any flash messages
            o.messages.clear();
            for (var level in data.messages) {
                for (var i=0; i<data.messages[level].length; i++) {
                    o.messages[level](data.messages[level][i]);
                }
            }
            o.basket.is_form_being_submitted = false;
        },
        showVoucherForm: function() {
            $('#voucher_form_container').show();
            $('#voucher_form_link').hide();
            $('#id_code').focus();
        },
        hideVoucherForm: function() {
            $('#voucher_form_container').hide();
            $('#voucher_form_link').show();
        },
        checkAndSubmit: function($ele, formPrefix, idSuffix) {
            if (o.basket.is_form_being_submitted) {
                return;
            }
            var formID = $ele.attr('data-id');
            var inputID = '#id_' + formPrefix + '-' + formID + '-' + idSuffix;
            $(inputID).attr('checked', 'checked');
            $ele.closest('form').submit();
            o.basket.is_form_being_submitted = true;
        }
    };

    o.checkout = {
        gateway: {
            init: function() {
                var radioWidgets = $('form input[name=options]');
                var selectedRadioWidget = $('form input[name=options]:checked');
                o.checkout.gateway.handleRadioSelection(selectedRadioWidget.val());
                radioWidgets.change(o.checkout.gateway.handleRadioChange);
                $('#id_username').focus();
            },
            handleRadioChange: function() {
                o.checkout.gateway.handleRadioSelection($(this).val());
            },
            handleRadioSelection: function(value) {
                var pwInput = $('#id_password');
                if (value == 'anonymous' || value =='new') {
                    pwInput.attr('disabled', 'disabled');
                } else {
                    pwInput.removeAttr('disabled');
                }
            }
        }
    };

    o.datetimepickers = {
        init: function() {
            o.datetimepickers.initDatePickers(window.document);
        },
        options: {
            'languageCode': 'en',
            'dateFormat': 'yy-mm-dd',
            'timeFormat': 'hh:ii',
            'datetimeFormat': 'yy-mm-dd hh:ii',
            'stepMinute': 15,
        },
        initDatePickers: function(el) {
            if ($.fn.datetimepicker) {
                var defaultDatepickerConfig = {
                    'format': o.datetimepickers.options.dateFormat,
                    'autoclose': true,
                    'language': o.datetimepickers.options.languageCode,
                    'minView': 2
                };
                var $dates = $(el).find('[data-oscarWidget="date"]').not('.no-widget-init').not('.no-widget-init *');
                $dates.each(function(ind, ele) {
                    var $ele = $(ele),
                        config = $.extend({}, defaultDatepickerConfig, {
                            'format': $ele.data('dateformat')
                        });
                    $ele.datetimepicker(config);
                });

                var defaultDatetimepickerConfig = {
                    'format': o.datetimepickers.options.datetimeFormat,
                    'minuteStep': o.datetimepickers.options.stepMinute,
                    'autoclose': true,
                    'language': o.datetimepickers.options.languageCode
                };
                var $datetimes = $(el).find('[data-oscarWidget="datetime"]').not('.no-widget-init').not('.no-widget-init *');
                $datetimes.each(function(ind, ele) {
                    var $ele = $(ele),
                        config = $.extend({}, defaultDatetimepickerConfig, {
                            'format': $ele.data('datetimeformat'),
                            'minuteStep': $ele.data('stepminute')
                        });
                    $ele.datetimepicker(config);
                });

                var defaultTimepickerConfig = {
                    'format': o.datetimepickers.options.timeFormat,
                    'minuteStep': o.datetimepickers.options.stepMinute,
                    'autoclose': true,
                    'language': o.datetimepickers.options.languageCode
                };
                var $times = $(el).find('[data-oscarWidget="time"]').not('.no-widget-init').not('.no-widget-init *');
                $times.each(function(ind, ele) {
                    var $ele = $(ele),
                        config = $.extend({}, defaultTimepickerConfig, {
                            'format': $ele.data('timeformat'),
                            'minuteStep': $ele.data('stepminute'),
                            'startView': 1,
                            'maxView': 1,
                            'formatViewType': 'time'
                        });
                    $ele.datetimepicker(config);
                });
            }
        }
    };


    o.init = function() {
        o.forms.init();
        o.datetimepickers.init();
        o.page.init();
        o.responsive.init();
        o.responsive.initSlider();
        o.compatibility.init();
    };

    return o;

})(oscar || {}, jQuery);
