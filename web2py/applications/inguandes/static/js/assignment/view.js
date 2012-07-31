(function (window) {
    'use strict';
    var $ = window.jQuery,
            INGUANDES = window.INGUANDES;
            
    function splitFilename(filename) {
        var ext,
            onlyname;
        ext = filename.split('.').pop();
        onlyname = filename.substring(0, filename.lastIndexOf('.'));
        
        return {name: onlyname, ext: ext}
    }

    function addNewFile(file) {
        var row_file,
            table_new_files = $('#tb-new-files tbody'),
            split,
            fileindex,
            file_size;
        
        split = splitFilename(file.name);
        
        if (INGUANDES.allowed_ext.length == 0 || $.inArray(split.ext, INGUANDES.allowed_ext) != -1) {    
            file_size = file.size/1024;
            
            if (file_size <= INGUANDES.max_size) {        
                INGUANDES.new_files.push(file);
                fileindex = INGUANDES.new_files.indexOf(file);
            
                row_file = $('#tr-new-file-template').clone();
                row_file.attr('id', 'tr-new-file-' + fileindex);
                
                row_file.find('td[data-name]').text(split.name);
                row_file.find('td[data-extension]').text(split.ext);
                row_file.find('td[data-size]').text(Math.round(file_size) + ' KB');
                
                row_file.find('[data-remove-file]')
                        .on('click', {
                            fileindex: fileindex
                        }, removeNewFile);

                row_file.find('[rel="tooltip"]').tooltip();
                
                table_new_files.append(row_file);
            }
            else {
                INGUANDES.notify('error', 'El archivo <strong>' + file.name + '</strong> es más grande que lo permitido.');
            }
        }
        else {
            INGUANDES.notify('error', 'El archivo <strong>' + file.name + '</strong> no es de un tipo permitido.');
        }
    }

    function removeNewFile(event) {    
        var fileindex = event.data.fileindex,
            row_file = $('#tr-new-file-' + fileindex);
                
        event.preventDefault();
        
        INGUANDES.new_files.splice(fileindex,1);
        
        row_file.find('[rel="tooltip"]').tooltip('hide');    
        row_file.remove();
    }

    function startUploadFiles(event) {
        var jqXHR,
            bar = $('#upload-progress');
            
        event.preventDefault();
        
        if (!INGUANDES.allowed_multiple && INGUANDES.new_files.length > 1) {
            INGUANDES.notify('error', 'Este trabajo permite un solo archivo.');
        }
        else {
            bar.removeClass('hide');
            $('#upload-progress .bar').css(
                'width',
                0 + '%'
            );
            
            jqXHR = $('#form-file-upload').fileupload('send', {files: INGUANDES.new_files})
                .success(uploadEnd)
                .error(uploadError);
        }
    }

    function uploadEnd(result, textStatus, jqXHR) {        
        var bar = $('#upload-progress'),
            table_new_files = $('#tb-new-files tbody');
        bar.fadeOut(800);
        
        if (result.hasOwnProperty("code")) {
            INGUANDES.notify('error', result.message);
        }
        else {        
            $.each(result, function (index, file) {    
                INGUANDES.all_files.push(file);
                addFile(file);
            });
            
            INGUANDES.new_files = []
            table_new_files.empty();
            
            INGUANDES.notify('success', 'Archivos enviados correctamente.');
        }
    }

    function uploadError(jqXHR, textStatus, errorThrown) {
        var bar = $('#upload-progress');        
        bar.fadeOut(200);
        INGUANDES.notify('error', 'Hubo un error al subir los archivos.');
    }

    function updateProgress(e, data) {
        var progress = parseInt(data.loaded / data.total * 100, 10);    
        $('#upload-progress .bar').css(
            'width',
            progress + '%'
        );
    }

    function addFile(file) {
        var row_file,
            table_files = $('#tb-files tbody');
            
        if (file.hasOwnProperty('history')) {
            $.each(file.history, function (index, fileid) {    
                removeFileRow(fileid);
            });
        }
                
        row_file = $('#tr-file-template').clone();
        row_file.attr('id', 'tr-file-' + file.id);
        
        row_file.find('td[data-name]').html('<a rel="tooltip" title="Descargar archivo" href="' + INGUANDES.api_url + 'download_user_assignment_file/' + file.href_arg + '" tagret="_blank">' + file.filename + '</a>');
        row_file.find('td[data-extension]').text(file.type);
        row_file.find('td[data-size]').text(file.size + ' KB');
        row_file.find('td[data-uploaded]').text(file.uploaded);
        
        if (INGUANDES.is_available) {        
            row_file.find('[data-remove-file]')
                    .on('click', {
                        fileid: file.id
                    }, removeFile);
        }
        else {
            row_file.find('[data-remove-file]').addClass('hide');
        }
                
        row_file.find('[data-history-file]')
                .on('click', {
                    fileid: file.id
                }, showFileHistory);

        row_file.find('[rel="tooltip"]').tooltip();
        
        table_files.append(row_file);
    }

    function removeFile(event) {    
        var fileid = event.data.fileid;
                
        event.preventDefault();
        
        $.ajax({
            url: INGUANDES.api_url + 'assignment_files/' + fileid,
            type: 'DELETE',
            success: function (data) {
                INGUANDES.notify('success', 'Archivo eliminado');
                removeFileRow(fileid);
            }
        });
    }
    
    function removeFileRow(fileid) {
        var row_file = $('#tr-file-' + fileid);
        row_file.find('[rel="tooltip"]').tooltip('hide');    
        row_file.remove();
    }
    
    function showFileHistory(event) {
        var fileid = event.data.fileid,
            history_container = $('#file-history-container'),
            history_list = history_container.find('ul'),
            ofile,
            hfile;
        
        event.preventDefault();
        
        ofile = findFileById(fileid);        
        history_container.find('#history-filename').text(ofile.filename + ofile.type);
        history_list.empty();
        
        $.each(ofile.history, function (index, hfileid) {    
            hfile = findFileById(hfileid); 
            history_list.append('<li>' + hfile.uploaded + ' (' + hfile.size + ' KB)</li>');
        });
        
        history_container.removeClass('hide');
    }
    
    function findFileById(fileid) {
        var results = $.grep(INGUANDES.all_files, function(f, i) {
            return f.id == fileid;
        });
        
        return results[0];
    }
            
    $(document).ready( function () {
        $('#form-file-upload').fileupload({
            dataType: 'json',
            type: 'POST',
            add: function (e, data) {            
                $.each(data.files, function (index, file) {    
                    addNewFile(file);
                });
            },
            progressall: updateProgress
        });
        
        $('#start-upload').on('click', startUploadFiles);
        
        $.each(INGUANDES.all_files, function (index, file) {    
            if (file.available == true) {
                addFile(file);
            }
        });
    });
}(this));