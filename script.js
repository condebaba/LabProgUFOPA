const form = document.querySelector('#pet-form');
const tipo = document.querySelector('#tipo');
const nome = document.querySelector('#nome');
const raca = document.querySelector('#raca');
const nascimento = document.querySelector('#nascimento');
const foto = document.querySelector('#foto');
const limpar = document.querySelector('#limpar');

const carteira = document.querySelector('#carteira');
const badgeTipo = document.querySelector('#badge-tipo');
const cardNome = document.querySelector('#card-nome');
const cardRaca = document.querySelector('#card-raca');
const cardNascimento = document.querySelector('#card-nascimento');
const fraseTipo = document.querySelector('#frase-tipo');
const photoFrame = document.querySelector('#photo-frame');
const preview = document.querySelector('#preview');

const textosPorTipo = {
  cao: {
    label: 'Cão',
    classe: 'dog',
    frase: 'Companheiro fiel e cheio de energia',
    emoji: '🐶',
  },
  gato: {
    label: 'Gato',
    classe: 'cat',
    frase: 'Felino curioso, elegante e independente',
    emoji: '🐱',
  },
};

function formatarData(valor) {
  if (!valor) {
    return 'dd/mm/aaaa';
  }

  const [ano, mes, dia] = valor.split('-');
  return `${dia}/${mes}/${ano}`;
}

function atualizarCarteira() {
  const dadosTipo = textosPorTipo[tipo.value];

  carteira.classList.remove('dog', 'cat');
  carteira.classList.add(dadosTipo.classe);
  badgeTipo.textContent = dadosTipo.label;
  document.querySelector('.paw').textContent = dadosTipo.emoji;
  fraseTipo.textContent = dadosTipo.frase;

  cardNome.textContent = nome.value.trim() || 'Nome do pet';
  cardRaca.textContent = raca.value.trim() || 'Raça do pet';
  cardNascimento.textContent = formatarData(nascimento.value);
}

function carregarFoto() {
  const arquivo = foto.files?.[0];

  if (!arquivo) {
    preview.removeAttribute('src');
    photoFrame.classList.remove('has-photo');
    return;
  }

  const leitor = new FileReader();
  leitor.addEventListener('load', () => {
    preview.src = leitor.result;
    photoFrame.classList.add('has-photo');
  });
  leitor.readAsDataURL(arquivo);
}

form.addEventListener('input', atualizarCarteira);
tipo.addEventListener('change', atualizarCarteira);
foto.addEventListener('change', carregarFoto);

limpar.addEventListener('click', () => {
  form.reset();
  carregarFoto();
  atualizarCarteira();
});

atualizarCarteira();
