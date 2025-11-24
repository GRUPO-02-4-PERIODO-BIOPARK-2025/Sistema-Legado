document.addEventListener('DOMContentLoaded', function () {

  function setError(el, msg) {
    if (!el) return;
    el.textContent = msg || '';
    if (msg) el.classList.add('visible');
    else el.classList.remove('visible');
  }

  function setInputInvalid(input, invalid) {
    if (!input) return;
    if (invalid) input.classList.add('input-invalid');
    else input.classList.remove('input-invalid');
  }

  // ===== PREÇO =====
  const precoInput = document.querySelector('input[name="preco"]');
  const precoError = document.getElementById('preco-error');

  if (precoInput) {
    precoInput.addEventListener('blur', function () {
      const valor = parseFloat(precoInput.value.replace(',', '.'));

      if (isNaN(valor) || valor < 0) {
        setError(precoError, 'Preço inválido.');
        setInputInvalid(precoInput, true);
      } else {
        setError(precoError, '');
        setInputInvalid(precoInput, false);
      }
    });
  }

  // ===== PESO =====
  const pesoInput = document.querySelector('input[name="peso"]');
  const pesoError = document.getElementById('peso-error');

  if (pesoInput) {
    pesoInput.addEventListener('blur', function () {
      if (pesoInput.value.trim() === '') {
        setError(pesoError, '');
        setInputInvalid(pesoInput, false);
        return;
      }

      const peso = parseFloat(pesoInput.value.replace(',', '.'));

      if (isNaN(peso) || peso < 0) {
        setError(pesoError, 'Peso inválido.');
        setInputInvalid(pesoInput, true);
      } else {
        setError(pesoError, '');
        setInputInvalid(pesoInput, false);
      }
    });
  }

});
