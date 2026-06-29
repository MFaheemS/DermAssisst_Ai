/* DermAssist-AI — main.js */

// Auto-dismiss alerts after 5 s
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert.alert-dismissible').forEach(el => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    }, 5000);
  });

  // Image preview on file input change
  const imageInput = document.getElementById('imageInput');
  if (imageInput) {
    imageInput.addEventListener('change', function () {
      const file = this.files[0];
      if (!file) return;
      const preview = document.getElementById('imagePreview');
      if (preview) {
        preview.src = URL.createObjectURL(file);
        preview.classList.remove('d-none');
      }
    });
  }

  // Drag-and-drop zone
  const zone = document.getElementById('uploadZone');
  if (zone) {
    ['dragenter', 'dragover'].forEach(ev =>
      zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.add('dragover'); })
    );
    ['dragleave', 'drop'].forEach(ev =>
      zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.remove('dragover'); })
    );
    zone.addEventListener('drop', e => {
      const file = e.dataTransfer.files[0];
      if (file && imageInput) {
        const dt = new DataTransfer();
        dt.items.add(file);
        imageInput.files = dt.files;
        imageInput.dispatchEvent(new Event('change'));
      }
    });
  }
});
