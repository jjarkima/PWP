"use strict";

const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

function renderMsg(msg) {
    $("div.notification").html("<p class='msg'>" + msg + "</p>");
}

function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

function sendData(href, method, item, postProcessor) {
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
}

function sensorRow(item) {
    let link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderSensor)'>edit</a>"+
                " | <a href='" + //uutta
                item["@controls"].self.href +
                "' onClick='deleteResource(event, this)'>delete</a>"; //end uutta
    console.log(item.header+","+item.message+","+item.date+","+item.user_id+","+link);
    return "<tr><td>" + item.header +
            "</td><td>" + item.message +
            "</td><td>" + item.date +
			"</td><td>" + item.user_id +
            "</td><td>" + link + "</td></tr>";
}

function messageRow(item) {
    return "<tr><td>" + item.message +
            "</td><td>" + item.date +
            "</td><td>" + item.user_id +
			"</td><td>" + item.parent_topic_id;
}

function userRow(item) {
    return "<tr><td>" + item.name +
            "</td><td>" + item.password;
}

function appendSensorRow(body) {
    $(".resulttable tbody").append(sensorRow(body));
}

function getSubmittedSensor(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendSensorRow);
    }
}

function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

function submitSensor(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.header = $("input[name='header']").val();
    data.message = $("input[name='message']").val();
	data.date = $("input[name='date']").val();
	data.user_id = parseInt($("input[name='user_id']").val());
	//logger gang
	console.log(form.attr("action")+","+form.attr("method")+","+JSON.stringify(data));
	//
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedSensor);
}

function deleteResource(event, a) {
    event.preventDefault();
    let resource = $(a);
    $.ajax({
        url:resource.attr("href"),
        type:"DELETE",
        success: function(){
            renderMsg("Delete Succesful");
        },
        error:renderError
    });
    location.reload();
}

function updateResource(event, a) {
    event.preventDefault();
    let resource = $(a);
    $.ajax({
        url:resource.attr("href"),
        type:"PUT",
        success: function(){
            renderMsg("Update Succesful");
        },
        error:renderError
    });
    location.reload(); //not necessary
}

function renderSensorForm(ctrl,hdr) {
    let form = $("<form>");
    let header = ctrl.schema.properties.header;
    let message = ctrl.schema.properties.message;
	let date = ctrl.schema.properties.date;
    let user_id = ctrl.schema.properties.user_id;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitSensor);
    form.append("<label>" + hdr + "</label>");
    form.append("<label>" + header.description + "</label>");
    form.append("<input type='text' name='header'>");
    form.append("<label>" + message.description + "</label>");
    form.append("<input type='text' name='message'>");
	form.append("<label>" + date.description + "</label>");
    form.append("<input type='text' name='date'>");
    form.append("<label>" + user_id.description + "</label>");
    form.append("<input type='text' name='user_id'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function renderSensor(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].collection.href +
        "' onClick='followLink(event, this, renderSensors)'>collection</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    $(".resulttable2 thead").empty();
    $(".resulttable2 tbody").empty();
    $(".resulttable3 thead").empty();
    $(".resulttable3 tbody").empty();

    renderSensorForm(body["@controls"].edit,"EDIT TOPIC");
    $("input[name='name']").val(body.name);
    $("input[name='model']").val(body.model);
    $("form input[type='submit']").before(
    );
}

function renderSensors(body) {
    $("div.navigation").empty();
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>header</th><th>message</th><th>date</th><th>user_id</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(sensorRow(item));
    });
    renderSensorForm(body["@controls"]["board:add-topic"],"SUBMIT NEW TOPIC");
}

function renderMessages(body) {
    $(".resulttable2 thead").html(
        "<tr><th>message</th><th>date</th><th>user_id</th><th>parent_topic_id</th></tr>"
    );
    let tbody = $(".resulttable2 tbody");
    body.items.forEach(function (item) {
        tbody.append(messageRow(item));
    });
}

function renderUsers(body) {
    $(".resulttable3 thead").html(
        "<tr><th>name</th><th>password</th></tr>"
    );
    let tbody = $(".resulttable3 tbody");
    body.items.forEach(function (item) {
        tbody.append(userRow(item));
    });
}

$(document).ready(function () {
    getResource("http://localhost:5000/api/topics/", renderSensors);
    getResource("http://localhost:5000/api/messages/", renderMessages);
    getResource("http://localhost:5000/api/users/", renderUsers);
});
