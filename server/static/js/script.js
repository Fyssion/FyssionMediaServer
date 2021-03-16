function copyToClipboard(element) {
  var $temp = $("<input>");
  $("body").append($temp);
  $temp.val($(element).prop("href")).select();
  document.execCommand("copy");
  $temp.remove();
}

function show_success(message) {
  var dialog = bootbox.dialog({
    message: message,
    className: 'modal modal-success fade-in',
    okButton: false
  });
}
