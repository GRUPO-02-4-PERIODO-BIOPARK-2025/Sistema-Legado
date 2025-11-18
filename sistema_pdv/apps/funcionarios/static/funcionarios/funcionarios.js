// Client-side validation for funcionarios form
document.addEventListener('DOMContentLoaded', function () {
  function digitsOnly(value) {
    return (value || '').toString().replace(/\D/g, '');
  }

  function setError(el, msg) {
    if (!el) return;
    el.textContent = msg || '';
    if (msg) el.classList.add('visible'); else el.classList.remove('visible');
  }

  function setInputInvalid(input, invalid) {
    if (!input) return;
    if (invalid) input.classList.add('input-invalid'); else input.classList.remove('input-invalid');
  }

  var cpfInput = document.querySelector('input[name="cpf"]');
  var cpfError = document.getElementById('cpf-error');
  if (cpfInput) {
    cpfInput.addEventListener('blur', function () {
      var digits = digitsOnly(cpfInput.value);
      if (digits.length !== 11) {
        setError(cpfError, 'CPF inválido: deve conter 11 dígitos.');
        setInputInvalid(cpfInput, true);
      } else {
        setError(cpfError, '');
        setInputInvalid(cpfInput, false);
      }
    });
    cpfInput.addEventListener('input', function () { 
      setError(cpfError, ''); 
      setInputInvalid(cpfInput, false); 
    });
  }

  var emailInput = document.querySelector('input[name="email"]');
  var emailError = document.getElementById('email-error');
  if (emailInput) {
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    emailInput.addEventListener('blur', function () {
      var v = (emailInput.value || '').trim();
      if (v === '') {
        setError(emailError, '');
        setInputInvalid(emailInput, false);
        return;
      }
      if (!emailRegex.test(v)) {
        setError(emailError, 'E-mail inválido. Verifique o formato.');
        setInputInvalid(emailInput, true);
      } else {
        setError(emailError, '');
        setInputInvalid(emailInput, false);
      }
    });
    emailInput.addEventListener('input', function () { 
      setError(emailError, ''); 
      setInputInvalid(emailInput, false); 
    });
  }
});
