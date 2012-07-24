(function (window) {
    'use strict';
    var $ = window.jQuery,
            INGUANDES = window.INGUANDES;
            
    function addNewContent (event) {
        var modal, 
            contentType, 
            cgId,
            data = $(event.currentTarget).data();            
        
        contentType = data.newContentType;
        cgId = data.cgId;
        
        modal = $('#modal-new-content-' + contentType);
        modal.find('.content-group-id').val(cgId);
        
        modal.modal('show');
    }
            
    $(document).ready( function () {
        INGUANDES.startDateFields();
    
        $("[rel=tooltip]").tooltip({placement: 'top'});
        $("[rel=popover]").popover();
        $(".collapse").collapse();
        
        $('.modal .modal-action').click( function () {
            $(this).closest('.modal').find('form').submit();
        });
        
        $('#modal-show-video').on('hidden', function () {
            $(this).find('#video-content-url').removeAttr('src');
        });
        
        $('[data-btn-type="new-content"]').click( addNewContent );
        
        $('[data-content-type="video"]').click( function ( event ) {
            var modal, videoName, videoUrl;
            
            data = $(event.currentTarget).data();
            videoName = data.contentName;
            videoUrl = data.contentUrl;
            
            console.log(videoUrl);
            
            modal = $('#modal-show-video');
            modal.find('#video-content-name').text(videoName);
            modal.find('#video-content-url').attr({src : videoUrl});
            
            modal.modal('show');
        });    
        
        $('#new-quiz-add-category').click( function ( event ) {
            var form = $(event.currentTarget).closest('form'),
                category = form.find('#quiz-category'),
                quantity = form.find('#quiz-category-count'),
                category_table = $('#new-quiz-categories-table'),
                str_td;
            str_td = '<tr>';
            str_td += '<td>' + category.val() + '</td>';
            str_td += '<td>' + quantity.val() + '</td>';
            str_td += '<td><a class="btn" rel="tooltip" title="Eliminar categoría del quiz"><i class="icon-remove"></i></a></td>';
            str_td += '</tr>';
                
            category_table.append($(str_td));
                    
            INGUANDES.quiz_categories[category.val()] = quantity.val();
            
            category.val('');
            quantity.val('');
            
            category_table.find("[rel=tooltip]").tooltip({placement: 'top'});
        });
        
        $('#modal-new-quiz').on('show', function () {
            var form = $(event.currentTarget).closest('form'),
                category = form.find('#quiz-category'),
                quantity = form.find('#quiz-category-count'),
                category_table = $('#new-quiz-categories-table');
                
            category.val('');
            quantity.val('');
            category_table.find('tbody').find('tr').remove();     
            INGUANDES.quiz_categories = {};        
        });

        $('.new-quiz-action').click( function () {
            var modal = $(this).closest('.modal'),
                formQuiz = $('#quiz-main-form'),
                method_url = formQuiz.attr('action'),
                new_quiz = {};
                
            new_quiz.name = formQuiz.find('#quiz-name').val();
            new_quiz.starting = formQuiz.find('#quiz-starting').val();
            new_quiz.ending = formQuiz.find('#quiz-ending').val();
            new_quiz.instance = formQuiz.find('#quiz-instanceid').val();        
            $.each(INGUANDES.quiz_categories, function (k,v) {
                new_quiz[k] = v;
            });
            
            $.ajax({
                    url: INGUANDES.api_url + 'quiz',
                    type: 'POST',
                    dataType: 'json',
                    data: new_quiz,
                    error: function (jqXHR, textStatus, errorThrown) {
                        // TODO: Avisar que hubo un error de forma mas profesional
                        INGUANDES.notify('error', 'No fue possible crear el quiz.');
                    },
                    success: function (data, textStatus, jqXHR) {
                        // TODO: Actualizar lista de quiz
                        INGUANDES.notify('success', 'El quiz se creó correctamente: ' + data.message);
                    }
                });
            
            modal.modal('hide');
        });
    });
}(this));