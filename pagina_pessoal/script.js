const botao = document.getElementById('meubotao'); // Busca um elemento da pagina pelo seu ID
const mensagemdiv = document.getElementById('mensagem'); // Busca um elemento da pagina pelo seu ID

const mensagens = [ // constante que contem as mensagens
    "Você é capaz de grandes coisas!",
    "Boa Vista tem um futuro programador top!",
    "Cada código escrito te torna melhor!",
    "A persistência leva ao sucesso!",
    "Hoje você deu mais um passo rumo aos seus objetivos!"
]

function monstrarmensagem() { // Função que monstra as mensagem
    const mensagemAleatoria = mensagens[Math.floor(Math.random() * mensagens.length)];

    mensagemdiv.textContent = mensagemAleatoria // mensagemdiv recebe as mensagem na div
    mensagemdiv.style.display = 'block'; // Faz a div ficar visível 
}
// Evento que faz a mensagem aparecer na tela depois do clique
botao.addEventListener('click', monstrarmensagem) 