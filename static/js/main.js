document.addEventListener('DOMContentLoaded', () => {
  // Cerrar alertas
  const closeButtons = document.querySelectorAll('.alert .close');
  closeButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      this.closest('.alert').remove();
    });
  });

  // Auto-cerrar alertas después de 5 segundos
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.remove();
    }, 5000);
  });

  // Confirmar eliminación de carrito
  const deleteButtons = document.querySelectorAll('form[action*="eliminar-carrito"]');
  deleteButtons.forEach(form => {
    form.addEventListener('submit', function(e) {
      if (!confirm('¿Estás seguro de que deseas eliminar este producto?')) {
        e.preventDefault();
      }
    });
  });
});
