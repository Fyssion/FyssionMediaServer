function copyToClipboard(element) {
  var $temp = $("<input>");
  $("body").append($temp);
  $temp.val($(element).prop("href")).select();
  document.execCommand("copy");
  $temp.remove();
}
