document.addEventListener('DOMContentLoaded',()=>{
  // Manejo simple de formularios (guardar en localStorage)
  const loginForm=document.getElementById('loginForm');
  const registerForm=document.getElementById('registerForm');
  const pedidoForm=document.getElementById('pedidoForm');

  if(loginForm){
    loginForm.addEventListener('submit',e=>{
      e.preventDefault();
      alert('Bienvenido a la florería Josbet');
      window.location.href='menu.html';
    });
  }
  if(registerForm){
    registerForm.addEventListener('submit',e=>{
      e.preventDefault();
      alert('Cuenta creada. Bienvenido a la florería Josbet');
      window.location.href='menu.html';
    });
  }
  if(pedidoForm){
    pedidoForm.addEventListener('submit',e=>{
      e.preventDefault();
      const data=new FormData(pedidoForm);
      const pedido=Object.fromEntries(data.entries());
      const pedidos=JSON.parse(localStorage.getItem('pedidos')||'[]');
      pedidos.push(pedido);
      localStorage.setItem('pedidos',JSON.stringify(pedidos));
      const summary=document.getElementById('pedidoSummary');
      summary.innerHTML=`<h3>Pedido guardado</h3><pre>${JSON.stringify(pedido,null,2)}</pre>`;
      pedidoForm.reset();
    });
  }
});
