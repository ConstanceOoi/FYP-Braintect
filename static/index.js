function readURL(input) {
  var errorText = document.getElementById('errorText');
  if (input.files && input.files[0]) {
    var file = input.files[0];
    var allowedFormats = ['image/jpeg', 'image/png', 'image/jpg']; // Allowed file formats

    if (allowedFormats.indexOf(file.type) === -1) {
      errorText.textContent = 'Invalid file format. Please upload a JPG, JPEG, or PNG file.';
      $('.image-upload-wrap').hide(); // Hide the image upload container
      input.value = ''; // Clear the file input
      return; // Exit the function
    } else {
      errorText.textContent = ''; // Clear any previous error message
    }

    var reader = new FileReader();

    reader.onload = function(e) {
      $('.image-upload-wrap').hide();
      $('.file-upload-image').attr('src', e.target.result);
      $('.file-upload-content').show();
      $('.image-title').html(input.files[0].name);
    };

    reader.readAsDataURL(input.files[0]);

  } else {
    removeUpload();
  }
}
  
  function removeUpload() {
    $('.file-upload-input').replaceWith($('.file-upload-input').clone());
    $('.file-upload-content').hide();
    $('.image-upload-wrap').show();
  }
  $('.image-upload-wrap').bind('dragover', function () {
          $('.image-upload-wrap').addClass('image-dropping');
      });
      $('.image-upload-wrap').bind('dragleave', function () {
          $('.image-upload-wrap').removeClass('image-dropping');
  });

