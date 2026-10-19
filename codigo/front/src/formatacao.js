// Máscaras de documentos. A pontuação é só visual: antes de enviar para a
// API os valores são limpos com apenasDigitos/limparRg.

// Encaixa os caracteres no padrão, em que "0" é a posição de um caractere.
// A pontuação só aparece quando há caracteres depois dela.
function mascarar(caracteres, padrao) {
  let resultado = "";
  let i = 0;
  for (const simbolo of padrao) {
    if (i >= caracteres.length) break;
    resultado += simbolo === "0" ? caracteres[i++] : simbolo;
  }
  return resultado;
}

export function apenasDigitos(valor = "") {
  return valor.replace(/\D/g, "");
}

// RG no formato 00.000.000-0: 8 dígitos e um dígito verificador, que pode ser X.
export function limparRg(valor = "") {
  let rg = "";
  for (const caractere of valor.toUpperCase()) {
    if (rg.length < 8 && /\d/.test(caractere)) rg += caractere;
    else if (rg.length === 8 && /[\dX]/.test(caractere)) rg += caractere;
  }
  return rg;
}

export function mascaraCpf(valor = "") {
  return mascarar(apenasDigitos(valor).slice(0, 11), "000.000.000-00");
}

export function mascaraCnpj(valor = "") {
  return mascarar(apenasDigitos(valor).slice(0, 14), "00.000.000/0000-00");
}

export function mascaraRg(valor = "") {
  return mascarar(limparRg(valor), "00.000.000-0");
}
