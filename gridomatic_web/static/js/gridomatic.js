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

function wait_for_task(data, cb) {
	var url = '/ajax/task/status/%s/'
	$().djcelery({task_id: data.task_id, on_success: cb})
}

function wait_then_refresh(data) {
	wait_for_task(data, function() {
		window.location.reload(true)
	})
}

function wait_then_goto(data, url) {
	wait_for_task(data, function() {
		window.location.href = url
	})
}

function redir_vm_list() {
		window.location.href = '/vm/list/'
}

$(document).ready(function() {
	$('.vm-start').click(function() {
		$(this).parent().spin('small')
		$(this).hide()
		$.post('/vm/start/', { 'uuid': $(this).attr("data-uuid") }, wait_then_refresh)
	})

	$('.vm-stop').click(function() {
		$(this).parent().spin('small')
		$(this).hide()
		$.post('/vm/stop/', { 'uuid': $(this).attr("data-uuid") }, wait_then_refresh)
	})

	$('.vm-destroy').click(function() {
		$(this).parent().spin('small')
		$(this).hide()
		$.post('/vm/destroy/', { 'uuid': $(this).attr("data-uuid") })
		setTimeout('redir_vm_list()', 1000);
	})

	$('.vm-restart').click(function() {
		$(this).parent().spin('small')
		$(this).hide()
		$.post('/vm/restart/', { 'uuid': $(this).attr("data-uuid") }, wait_then_refresh)
	})
})
