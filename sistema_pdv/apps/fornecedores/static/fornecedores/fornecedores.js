// Client-side validation and ViaCEP lookup for fornecedores form
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

  var cnpjInput = document.querySelector('input[name="cnpj"]');
  var cnpjError = document.getElementById('cnpj-error');
  if (cnpjInput) {
    cnpjInput.addEventListener('blur', function () {
      var digits = digitsOnly(cnpjInput.value);
      if (digits.length !== 11 && digits.length !== 14) {
        setError(cnpjError, 'CNPJ/CPF inválido: deve conter 11 (CPF) ou 14 (CNPJ) dígitos.');
        setInputInvalid(cnpjInput, true);
      } else {
        setError(cnpjError, '');
        setInputInvalid(cnpjInput, false);
      }
    });
    cnpjInput.addEventListener('input', function () { setError(cnpjError, ''); setInputInvalid(cnpjInput, false); });
  }

  var cepInput = document.querySelector('input[name="cep"]');
  var cepError = document.getElementById('cep-error');
  var enderecoInput = document.querySelector('input[name="endereco"]');
  var cidadeInput = document.querySelector('input[name="cidade"]');
  var estadoInput = document.querySelector('input[name="estado"]');
  var emailInput = document.querySelector('input[name="email"]');
  var emailError = document.getElementById('email-error');

  if (cepInput) {
    cepInput.addEventListener('blur', function () {
      var digits = digitsOnly(cepInput.value);
      if (digits.length !== 8) {
        setError(cepError, 'CEP inválido. Deve ter 8 dígitos.');
        setInputInvalid(cepInput, true);
        return;
      }
      setError(cepError, 'Buscando endereço...');
      // fetch ViaCEP
      fetch('https://viacep.com.br/ws/' + digits + '/json/')
        .then(function (res) { return res.json(); })
        .then(function (data) {
          if (data.erro) {
            setError(cepError, 'CEP não encontrado. Verifique o número.');
            setInputInvalid(cepInput, true);
            return;
          }
          // fill address fields
          if (enderecoInput && (data.logradouro || data.bairro)) {
            var endereco = [data.logradouro, data.bairro].filter(Boolean).join(', ');
            enderecoInput.value = endereco;
          }
          if (cidadeInput && data.localidade) cidadeInput.value = data.localidade;
          if (estadoInput && data.uf) estadoInput.value = data.uf;
          setError(cepError, '');
          setInputInvalid(cepInput, false);
        })
        .catch(function () {
          setError(cepError, 'Não foi possível buscar endereço (erro de rede).');
          setInputInvalid(cepInput, true);
        });
    });

    cepInput.addEventListener('input', function () { setError(cepError, ''); setInputInvalid(cepInput, false); });
  }

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
    emailInput.addEventListener('input', function () { setError(emailError, ''); setInputInvalid(emailInput, false); });
  }
});
