        $("body .selected").select2({width:'100%'});


        if($("body .selected").hasClass('required')){
            $("body .selected.required").next().children().children().addClass('required');
        }

        $('.modal').on('click', function(e){
            e.preventDefault();
            var url =  $(this).attr('href');

            $.ajax({
                method: "GET",
                url: url
            })
            .done(function( msg ) {
                $('#modal-id .uk-body-custom').html(msg);
                if($("body .selected").hasClass('required')){
                    $("body .selected.required").next().children().children().addClass('required');
                }
            });


        });

        $('.modal-full').on('click', function(e){
            e.preventDefault();
            var url =  $(this).attr('href');

            $.ajax({
                method: "GET",
                url: url
            })
            .done(function( msg ) {
                $('#modal-full .uk-body-custom').html(msg);
                if($(".selected").hasClass('required')){
                    $(".selected.required").next().children().children().addClass('required');
                }
            });


        });

        $('#modal-id').on('hide', function () {
            $('#modal-id .uk-body-custom').html('');
        });

        $('#modal-full').on('hide', function () {
            $('#modal-full .uk-body-custom').html('');
        });

        $('[data-toggle="datepicker"]').datepicker({
            zIndex:2000,
            format: 'dd/mm/yyyy'
        }).inputmask("date", { placeholder:"__/__/____"});

        $('body').on('click', '.select2-search__field', function(e){
            e.preventDefault();
        });

        $('body #dataTable, body table.display').on('click', 'tbody .uk-checkbox-item', function(e){
            var $check = $(this);
            var $parent = $check.parent().parent();
            if(!$check.is(':checked')){
                $parent.removeClass('uk-background-primary').attr({'style':''});
            }else{
                $parent.addClass('uk-background-primary').attr({'style':'color:#fff'});
            }

        });

        Waves.attach('.waves-effect', ['waves-block']);
        Waves.init();


        $('.count-to').countTo();

           // Datable excecution

        var table = $('#dataTable').DataTable({
            'language':{
                "sProcessing":     "Traitement en cours...",
                "sSearch":         "Rechercher&nbsp;:",
                "sLengthMenu":     "Afficher _MENU_ &eacute;l&eacute;ments",
                "sInfo":           "Affichage de  _START_ &agrave; _END_ sur _TOTAL_ ",
                "sInfoEmpty":      "Affichage de 0 &agrave; 0 sur 0 ",
                "sInfoFiltered":   "(filtr&eacute; de _MAX_ &eacute;l&eacute;ments au total)",
                "sInfoPostFix":    "",
                "sLoadingRecords": "Chargement en cours...",
                "sZeroRecords":    "Aucun &eacute;l&eacute;ment &agrave; afficher",
                "sEmptyTable":     "Aucune donn&eacute;e disponible",
                "oPaginate": {
                    "sFirst":      "Premier",
                    "sPrevious":   "Pr&eacute;c&eacute;dent",
                    "sNext":       "Suivant",
                    "sLast":       "Dernier"
                },
                "oAria": {
                    "sSortAscending":  ": activer pour trier la colonne par ordre croissant",
                    "sSortDescending": ": activer pour trier la colonne par ordre d&eacute;croissant"
                }
            },
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tous"]],
            "info": false,
            //"searching": false,
            "iDisplayLength": 25,
            //dom: 'f',
            "bLengthChange" : true
        });

        var table_display = $('table.display').DataTable({
            'language':{
                "sProcessing":     "Traitement en cours...",
                "sSearch":         "Rechercher&nbsp;:",
                "sLengthMenu":     "Afficher _MENU_ &eacute;l&eacute;ments",
                "sInfo":           "Affichage de  _START_ &agrave; _END_ sur _TOTAL_ ",
                "sInfoEmpty":      "Affichage de 0 &agrave; 0 sur 0 ",
                "sInfoFiltered":   "(filtr&eacute; de _MAX_ &eacute;l&eacute;ments au total)",
                "sInfoPostFix":    "",
                "sLoadingRecords": "Chargement en cours...",
                "sZeroRecords":    "Aucun &eacute;l&eacute;ment &agrave; afficher",
                "sEmptyTable":     "Aucune donn&eacute;e disponible",
                "oPaginate": {
                    "sFirst":      "Premier",
                    "sPrevious":   "Pr&eacute;c&eacute;dent",
                    "sNext":       "Suivant",
                    "sLast":       "Dernier"
                },
                "oAria": {
                    "sSortAscending":  ": activer pour trier la colonne par ordre croissant",
                    "sSortDescending": ": activer pour trier la colonne par ordre d&eacute;croissant"
                }
            },
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tous"]],
            "info": false,
            //"searching": false,
            "iDisplayLength": 10,
            //dom: 'f',
            "bLengthChange" : true
        });


        $('body').on('draw.dt', table, function() {

            $('body #dataTable tbody tr').each(function(){
                $link = $(this).data('link');
                if($link){
                    var exist_paged = $link.split("?");
                    console.log(exist_paged);
                    if (exist_paged.length >= 2){
                        paged = '?paged='+table.page.info().page;
                        $url = exist_paged[0]+paged;
                    }else{
                        paged = '?paged='+table.page.info().page;
                        $url = $link+paged;
                    }
                    $(this).data('link', $url);
                }
            });

            if(table.page.info()){
                window.history.pushState('page '+table.page.info().page, 'Title', window.location.pathname+'?paged='+table.page.info().page);
            }

        });



        $('body #dataTable').on('dblclick', 'tbody tr td', function () {
            lien = $(this).parent().data('link');
            if(lien){
                colIdx = table.cell(this).index().column;
                if (colIdx != 0 && lien){
                    window.location = lien;
                }
            }


        });

        $('body table.display').on('dblclick', 'tbody tr td', function () {
            lien = $(this).parent().data('link');
            if(lien){
                colIdx = table_display.cell(this).index().column;
                if (colIdx != 0 && lien){
                    window.location = lien;
                }
            }

        });

        $('body #dataTable').on('click', '.uk-checkbox-all', function(){

            var rows = table.rows({ 'search': 'applied' }).nodes();


            var $check = $('input.uk-checkbox-item', rows).prop('checked', this.checked);

            var $parent = $check.parent().parent();
            if($check.is(':checked')){
                $parent.addClass('uk-background-primary').attr({'style':'color:#fff'});
                $('.uk-div').removeClass('uk-hidden');
            }else{
                $parent.removeClass('uk-background-primary').attr({'style':''});
                $('.uk-div').addClass('uk-hidden');
            }

        });

        $('body table.display').on('click', '.uk-checkbox-all', function(){

            var rows = table_display.rows({ 'search': 'applied' }).nodes();


            var $check = $('input.uk-checkbox-item', rows).prop('checked', this.checked);

            //console.log(rows);

            var $parent = $check.parent().parent();
            if($check.is(':checked')){
                $parent.addClass('uk-background-primary').attr({'style':'color:#fff'});
                $('.uk-div').removeClass('uk-hidden');
            }else{
                $parent.removeClass('uk-background-primary').attr({'style':''});
                $('.uk-div').addClass('uk-hidden');
            }

        });


        $('#dataTable tbody, table.display tbody').on('change', 'input.uk-checkbox-item', function(){
          // If checkbox is not checked
          var rows = table.rows({ 'search': 'applied' }).nodes();
          var el = $('input.uk-checkbox-all').get(0);

          if(!this.checked){
             // If "Select all" control is checked and has 'indeterminate' property
             if(el && el.checked){
                // Set visual state of "Select all" control
                // as 'indeterminate'
                el.checked = false;

                //el.indeterminate = true;
             }

              count = 0;
              $('input.uk-checkbox-item').each(function(){
                  if($(this).is(':checked')){
                    count++;
                  }
              });

              if (count == 0){
                  $('.uk-div').addClass('uk-hidden');
              }

          }else{
              count = 0;
              $('input.uk-checkbox-item').each(function(){
                  if($(this).is(':checked')){
                    count++;
                  }
              });
              if (rows.length == count){
                  el.checked = true;
              }
              $('.uk-div').removeClass('uk-hidden');
          }
        });

        var reload = false;

        // function pour reactualiser la page si au besoin
        function reloading(){
            if(reload == true){
                window.location.reload(reload)
            }
        }

        // function de suppression des elements selectionnes sur le tableau
        $('body').on('click', '#deleted', function(e){
            e.preventDefault();
            var url =  $(this).attr('href');
            $.ajax({
                method: "POST",
                data: table.$('input.uk-checkbox-item').serialize(),
                url: url
            })
            .done(function( msg ) {

                msg = $.parseJSON(msg);
                var document = $("<p/>").addClass('uk-modal-body');
                $.each(msg, function(i, item){
                    if(item['statut'] == 'OK'){

                        for(var x=0; x<item['element'].length; x++){
                            $input = $('input[value='+item['element'][x]+']');
                            $parent = $input.parent().parent();
                            table.row($parent).remove().draw( false );
                        };

                        document.append(
                            $('<br/>')
                        ).append(
                            $('<div uk-alert style="margin:0;"/>').addClass('uk-alert-success').append(
                                $('<p/>').html(item['message'])
                            )
                        );
                        // activer la reactualisation de la page en cours
                        if(item['reload'] == 1){
                            reload = true;
                            reloading();
                        }

                    }
                    if(item['statut'] == 'NOK'){
                        document.append(
                            $('<br/>')
                        ).append(
                            $('<div uk-alert style="margin:0;"/>').addClass('uk-alert-warning').append(
                                $('<p/>').html(item['message'])
                            )
                        )
                    }
                });

                var rows = table.rows({ 'search': 'applied' }).nodes();
                $('input.uk-checkbox-item', rows).prop('checked', false).parent().parent().removeClass('uk-background-primary').attr({'style':''});

                UIkit.modal.dialog('<div class="uk-body-custom"></div>');
                document.appendTo('.uk-body-custom');
                $('.uk-div').addClass('uk-hidden');
                $('.uk-checkbox-all').prop('checked', false);

            });

        });

        // recherche sur DataTable
        $('#searchbox').on('keyup', function(){
            table.search($(this).val()).draw() ;
        });

        $('#searchbox_2').on('keyup', function(){
            table_display.search($(this).val()).draw() ;
        });


        // fixer la hauteur de la zone d'affichage 10, 20
        if($('#dataTable').width()){
            $('#dataTable_wrapper').css({width:$('#dataTable').width()});
        }else{
            $('#dataTable_wrapper').css({width:$('table.display').width()});
        }


        // click pour ouvrir une autre page en target="_blank"
        $('#print').on('click', function (e) {
            e.preventDefault();
            url = $(this).attr('href');
            window.open(url);
            window.location.reload();
        });

        $('.uk-target-blank').on('click', function (e) {
            e.preventDefault();
            url = $(this).attr('href');
            window.open(url);
        });

        $('.uk-actives').on('mouseover', function () {
            if($(this).hasClass('uk-button-success-active')){
                $(this).removeClass('uk-button-success-active').addClass('uk-button-danger-active');
            }
            else{
                $(this).removeClass('uk-button-danger-active').addClass('uk-button-success-active')
            }
        }).on('mouseleave', function () {
            if($(this).hasClass('uk-button-danger-active')){
                $(this).removeClass('uk-button-danger-active').addClass('uk-button-success-active')

            }
            else{
                $(this).removeClass('uk-button-success-active').addClass('uk-button-danger-active')
            }
        });