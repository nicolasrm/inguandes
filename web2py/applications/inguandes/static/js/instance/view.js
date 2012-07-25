(function (window) {
    'use strict';
    var $ = window.jQuery,
            INGUANDES = window.INGUANDES;
            
    function showNewContentModal (event) {
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
    
    function showEditContentModal (event) {
        var modal,            
            data = $(event.currentTarget).data(),
            cgId = data.cgId,
            cg_div = $('#collapse' + cgId),
            content_info,
            table_contents = $('#table-edit-content tbody');  
            
        table_contents.empty();
        
        INGUANDES.editable_contents = []
        $.each(cg_div.find('a[data-content-id]'), function (index, a_content) {
            content_info = $(a_content).data();
            addEditableContent(content_info);
            INGUANDES.editable_contents.push(content_info);
        });
        
        modal = $('#modal-edit-contents');
        modal.find('.content-group-id').val(cgId);
        
        modal.modal('show');
    }
    
    function addEditableContent (content) {
        var table_contents = $('#table-edit-content tbody'),
            row_content = $('#tr-edit-content-template').clone();
            
        row_content.attr('id', 'tr-edit-' + content.contentType + '-' + content.contentId);
        row_content.find('td[data-name]').html('<i class="icon-' + content.icon + '"></i> ' + content.contentName);
        
        if (content.contentRequired == 'T') {
            row_content.find('td[data-required]').html('<i class="icon-ok"></i>');
        }
        else {
            row_content.find('td[data-required]').html('<i class="icon-remove"></i>');
        }
            
        row_content.find('[data-edit-content]')
                .on('click', {
                    content: content
                }, editContentForm);
                
        row_content.find('[data-remove-content]')
                .on('click', {
                    content: content
                }, removeContentAlert);
            
        row_content.find('[rel="tooltip"]').tooltip();
            
        table_contents.append(row_content);
    }
    
    function editContentForm (event) {
        var form_container = $('#edit-content-form'),
            form = form_container.find('form'),
            content = event.data.content;
            
        form_container.removeClass('hide');
        form.find('#edit-content-name').val(content.contentName)
        form.find('#edit-content-description').val(content.contentDescription)
        if (content.contentRequired == 'T') {
            form.find('#edit-content-required').prop("checked", true);
        }
        else {
            form.find('#edit-content-required').prop("checked", false);
        }
    }
    
    function removeContentAlert (event) {
        var alert = $('#alert-renove-content'),
            content = event.data.content,
            confirm = $('#alert-remove-content-confirm');
        
        alert.find('#content-to-remove').text(content.contentName);
        
        confirm.on('click', {
                    content: content
                }, confirmRemoveContent);
        
        alert.show();
        alert.alert();
    }
    
    function confirmRemoveContent (event) {
        var alert = $('#alert-renove-content'),
            content = event.data.content;
            
        $.ajax({
            url: INGUANDES.api_url + 'remove_content/' + content.contentId + '/' + content.contentType,
            type: 'POST',
            success: function (data) {
                INGUANDES.notify('success', 'Contenido eliminado con éxito.');
                removeContent(content);
            },
            error: function (data) {
                INGUANDES.notify('error', 'No fue posible eliminar el contenido.');
            }
        });
            
        alert.alert('close');
    }
    
    function removeContent (content) {
        var row_content = $('#tr-edit-' + content.contentType + '-' + content.contentId),
            a_content = $('[data-content-id="' + content.contentId + '"][data-content-type="' + content.contentType + '"]');
            
        a_content.closest('li').remove();
        
            
        row_content.remove();
    }
    
    function showVideo (event) {
        var modal, videoName, videoUrl, data;
        
        data = $(event.currentTarget).data();
        videoName = data.contentName;
        videoUrl = data.contentUrl;
        
        console.log(videoUrl);
        
        modal = $('#modal-show-video');
        modal.find('#video-content-name').text(videoName);
        modal.find('#video-content-url').attr({src : videoUrl});
        
        modal.modal('show');
    }
    
    function addQuizCategory (event) {
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
    }
    
    function prepareQuizModal () {
        var form = $(event.currentTarget).closest('form'),
            category = form.find('#quiz-category'),
            quantity = form.find('#quiz-category-count'),
            category_table = $('#new-quiz-categories-table');
            
        category.val('');
        quantity.val('');
        category_table.find('tbody').find('tr').remove();     
        INGUANDES.quiz_categories = {};        
    }
    
    function createQuiz () {
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
    }
            
    $(document).ready( function () {
        INGUANDES.startDateFields();
    
        $("[rel=tooltip]").tooltip({placement: 'top'});
        $("[rel=popover]").popover();
        $(".collapse").collapse();
        
        $('.modal .modal-action').click( function () {
            $(this).closest('.modal').find('form').submit();
        });
        
        $('[data-btn-type="new-content"]').click(showNewContentModal);
        $('[data-btn-type="edit-content"]').click(showEditContentModal);
        
        $('[data-content-type="video"]').click(showVideo);    
        $('#modal-show-video').on('hidden', function () {
            $(this).find('#video-content-url').removeAttr('src');
        });
        
        $('#new-quiz-add-category').click(addQuizCategory);        
        $('#modal-new-quiz').on('show', prepareQuizModal);
        $('.new-quiz-action').click(createQuiz);
    });
}(this));