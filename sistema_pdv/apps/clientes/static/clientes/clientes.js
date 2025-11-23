document.addEventListener('DOMContentLoaded', function () {

  function digitsOnly(value) {
    return (value || '').toString().replace(/\D/g, '');
  }

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

  // ===== CNPJ / CPF =====
  const cnpjInput = document.querySelector('input[name="cpf_cnpj"]');
  const cnpjError = document.getElementById('cpf-cnpj-error');

  if (cnpjInput) {
    cnpjInput.addEventListener('blur', function () {
      const digits = digitsOnly(cnpjInput.value);

      if (digits.length !== 11 && digits.length !== 14) {
        setError(cnpjError, 'CPF/CNPJ inválido. Deve ter 11 (CPF) ou 14 (CNPJ) dígitos.');
        setInputInvalid(cnpjInput, true);
      } else {
        setError(cnpjError, '');
        setInputInvalid(cnpjInput, false);
      }
    });

    cnpjInput.addEventListener('input', function () {
      setError(cnpjError, '');
      setInputInvalid(cnpjInput, false);
    });
  }

  // ===== CEP + ViaCEP =====
  const cepInput = document.querySelector('input[name="cep"]');
  const cepError = document.getElementById('cep-error');
  const enderecoInput = document.querySelector('input[name="endereco"]');
  const cidadeInput = document.querySelector('input[name="cidade"]');
  const estadoInput = document.querySelector('input[name="estado"]');

  if (cepInput) {
    cepInput.addEventListener('blur', function () {
      const digits = digitsOnly(cepInput.value);

      if (digits.length !== 8) {
        setError(cepError, 'CEP inválido. Deve conter 8 dígitos.');
        setInputInvalid(cepInput, true);
        return;
      }

      setError(cepError, 'Buscando endereço...');

      fetch(`https://viacep.com.br/ws/${digits}/json/`)
        .then(res => res.json())
        .then(data => {

          if (data.erro) {
            setError(cepError, 'CEP não encontrado.');
            setInputInvalid(cepInput, true);
            return;
          }

          if (enderecoInput && data.logradouro)
            enderecoInput.value = `${data.logradouro} - ${data.bairro || ''}`;

          if (cidadeInput && data.localidade)
            cidadeInput.value = data.localidade;

          if (estadoInput && data.uf)
            estadoInput.value = data.uf;

          setError(cepError, '');
          setInputInvalid(cepInput, false);
        })
        .catch(() => {
          setError(cepError, 'Erro ao buscar CEP. Verifique sua conexão.');
          setInputInvalid(cepInput, true);
        });
    });

    cepInput.addEventListener('input', function () {
      setError(cepError, '');
      setInputInvalid(cepInput, false);
    });
  }

  // ===== EMAIL =====
  const emailInput = document.querySelector('input[name="email"]');
  const emailError = document.getElementById('email-error');
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (emailInput) {
    emailInput.addEventListener('blur', function () {
      const email = emailInput.value.trim();

      if (email === '') {
        setError(emailError, '');
        setInputInvalid(emailInput, false);
        return;
      }

      if (!emailRegex.test(email)) {
        setError(emailError, 'E-mail inválido.');
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
