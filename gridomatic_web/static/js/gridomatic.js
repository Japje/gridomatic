"use strict"

function csrfSafeMethod(method) {
	// these HTTP methods do not require CSRF protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))
}

$.ajaxSetup({
	crossDomain: false, // obviates need for sameOrigin test
	beforeSend: function(xhr, settings) {
		if (!csrfSafeMethod(settings.type)) {
			xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'))
		}
	}
})

function wait_for_task(data) {
	var url = '/ajax/task/status/%s/'
	console.log(data)
	$().djcelery({task_id: data.task_id, on_success: function() {
		window.location.reload(true)
	}})
}

$(document).ready(function() {
	$('.vm-start').click(function() {
		$(this).parent().spin('small')
		$(this).hide()
		$.post('/vm/start/', { 'uuid': $(this).attr("data-uuid") },	wait_for_task)
	})

	$('.vm-stop').click(function() {
		$(this).parent().spin('small')
		$(this).hide()
		$.post('/vm/stop/', { 'uuid': $(this).attr("data-uuid") },	wait_for_task)
	})

	$('.vm-destroy').click(function() {
		$(this).parent().spin('small')
		$(this).hide()
		$.post('/vm/destroy/', { 'uuid': $(this).attr("data-uuid") },	wait_for_task)
	})

	$('.vm-restart').click(function() {
		$(this).parent().spin('small')
		$(this).hide()
		$.post('/vm/restart/', { 'uuid': $(this).attr("data-uuid") },	wait_for_task)
	})
})
