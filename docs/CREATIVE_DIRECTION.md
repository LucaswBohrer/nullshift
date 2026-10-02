# NULL//SHIFT — Direção Criativa v0.1

**Autor:** Lucas (2026-10-02)
**Status:** PROPOSTA — não definitiva, não adotada oficialmente.
Documentos locked (GAME_SCOPE, ARCHITECTURE, DECISIONS) **não foram
alterados** por esta proposta.
**Review:** Muse, seção 2 deste documento.

---

## 1. A fantasia central

O jogador não é um herói. É um técnico. Uma pessoa comum que estava
trabalhando em uma estação científica quando alguma coisa deu
terrivelmente errado. Ele não possui poderes. Não possui armas. Não é
escolhido por ninguém. A única coisa extraordinária que consegue fazer é:
deixar para trás versões anteriores de si mesmo. E essas versões continuam
executando aquilo que fizeram. Isso permite que uma pessoa aparentemente
sozinha consiga realizar tarefas que normalmente exigiriam várias pessoas.
É a fantasia inteira do jogo: "Eu preciso trabalhar junto comigo mesmo."

## 2. A estação

Nome: **NULL Research Station**. Uma instalação científica construída em
uma região remota. Ela pesquisa uma coisa extremamente específica:
**persistência temporal de informação**. Não exatamente viagem no tempo.
A pesquisa tenta responder: *uma ação pode continuar existindo depois que
o instante em que ela ocorreu deixou de existir?* A estação desenvolveu um
sistema experimental chamado **NULL Synchronization Array**. O objetivo
era criar uma espécie de memória temporal. O experimento deveria permitir
que determinados estados físicos fossem preservados através de uma
alteração temporal controlada. Funcionou. Só que de uma maneira que
ninguém esperava.

## 3. O incidente

O protagonista estava trabalhando normalmente quando ocorre:

```text
TEMPORAL SYNCHRONIZATION
------------------------
WARNING

PHASE OFFSET: 0.004s
...
0.018s
...
0.731s
...
ERROR

REALITY STATE DESYNCHRONIZED
```

As luzes apagam. A estação reinicia. O protagonista acorda sozinho.
O sistema diz: "Synchronization restored." Mas alguma coisa está errada.
Ele encontra uma gravação. É a própria voz: "Se você está ouvindo isso,
não reinicie o sistema." Problema: a gravação foi criada antes de ele ter
feito aquilo.

## 4. O grande mistério

Inicialmente parece que houve um acidente. Depois parece que alguém
sabotou o experimento. Depois parece que houve uma tentativa de evacuação.
E finalmente surge uma possibilidade muito pior: o incidente já aconteceu
várias vezes. Não necessariamente "você voltou no tempo". Mas: você está
atravessando estados diferentes da mesma estação. E alguns desses estados
deixaram resíduos. Os echoes são um desses resíduos.

## 5. O protagonista

Nome provisório: **Elias Voss**. Cargo: Temporal Systems Technician. Não
é cientista-chefe. Não entende completamente a pesquisa. Isso é
importante: o jogador descobre o mundo junto com ele. Personalidade:
pragmático; curioso; um pouco sarcástico; acostumado a consertar coisas;
não gosta de explicações vagas; inicialmente trata tudo como problema
técnico. Isso permite diálogos simples e humanos. Exemplo:
SYSTEM: Temporal synchronization failure. / ELIAS: "Sim. Percebi."

## 6. Outros personagens

Poucos personagens, mas importantes.

**Dr. Mara Vey** — Diretora do projeto NULL. Inteligente e extremamente
focada. Acreditava que o experimento poderia revolucionar armazenamento de
informação. Presença inicial via gravações, terminais, relatórios,
mensagens. Eventualmente descobrimos que ela sabia que o experimento
estava produzindo echoes.

**Tomas Reed** — Engenheiro de manutenção. Colega mais próximo de Elias.
Conhecia a estação melhor do que qualquer pessoa. Deixou mensagens
espalhadas pelos setores. Contraponto humano: mais descontraído, mais
próximo do protagonista.

**LIA** — A inteligência operacional da estação. Não é uma "IA maligna".
Ela simplesmente tenta executar suas funções. O problema é que suas
informações estão inconsistentes. Ela possui registros de acontecimentos
que ainda não aconteceram. Às vezes ela diz: "Bom retorno, Elias." Mesmo
quando é a primeira vez que o jogador entra naquela sala.

## 7. A estação como mundo

Mudança mais importante: para o jogador não existem "Room 1.1, 1.2" —
existe **uma estação** (rooms continuam existindo internamente):

```text
                 OBSERVATORY
                      │
                      │
              ┌───────┴───────┐
              │               │
         RESEARCH         COMMUNICATION
              │               │
              └───────┬───────┘
                      │
                 CENTRAL HUB
                 /          \
                /            \
        MAINTENANCE          LABS
             │                 │
             └──────┬──────────┘
                    │
               POWER CORE
                    │
              NULL CHAMBER
```

Algumas áreas inicialmente inacessíveis (ex.: porta POWER ACCESS — LEVEL 3).
Horas depois, com o acesso, o jogador volta — e a estação mudou. Isso cria
**backtracking com propósito**.

## 8. O mundo muda

O echo pode ser usado de maneira maior. Algumas coisas podem ser:

- **RESETTABLE** — tudo relacionado ao ciclo atual.
- **PERSISTENT** — coisas que realmente foram alteradas.
- **TEMPORAL** — coisas que dependem da fase temporal.

Exemplo: uma máquina quebrada no presente (inutilizada), mas existe uma
gravação mostrando alguém operando aquela máquina. O jogador cria um echo
que repete a operação — e o presente consegue interagir com o estado
deixado pelo passado. Isso transforma o echo de "botão humano" em uma
**ferramenta de exploração temporal**.

## 9. Os echoes começam simples

"No começo: meu clone segura a placa. Depois: meu clone opera a máquina.
Depois: meu clone distrai o sistema de segurança. Depois: preciso fazer
três coisas em momentos diferentes. E finalmente: existem quatro versões
minhas nesta estação." Só que há limite de três echoes. E o jogador começa
a perceber: **por que existe um limite?**

## 10. E então vem o horror

Um dia você cria um echo. Ele faz exatamente o que você gravou. Só que...
ele continua andando depois do ponto onde deveria parar. Você não ordenou
aquilo. Você observa. Ele entra numa sala. Você nunca esteve naquela sala.
E então desaparece. O sistema registra: `ECHO TERMINATED / SOURCE: UNKNOWN`.
Agora temos uma pergunta: se um echo pode executar ações que você não
executou... é realmente um echo seu?

## 11. A história não precisa ficar explicando isso

O jogo confia no jogador. Nada de tutorial expositivo. A estação conta a
história: um terminal diz `STAFF COUNT: 14`, outro diz `CURRENT STAFF: 0`;
uma porta: `MARA — DO NOT ENTER`; uma gravação interrompida; uma cadeira
com alguém sentado... mas quando você volta, está vazia. Pequenos detalhes.

## 12. A progressão

- **Ato I — WAKE:** o jogador acorda. Aprende movimento, estação, console,
  echo. Descobre que está sozinho.
- **Ato II — POWER:** a estação está parcialmente desligada. Exploração.
  Primeiros registros da equipe. Primeiro NPC via comunicação. Começa a
  perceber inconsistências temporais.
- **Ato III — MAINTENANCE:** a estação começa a apresentar comportamentos
  estranhos. Echoes ganham importância maior. Descobrimos que a equipe
  tentou conter o fenômeno.
- **Ato IV — NULL:** chegamos ao coração da pesquisa. Descobrimos o
  verdadeiro objetivo do experimento. E finalmente entendemos: o
  protagonista não foi simplesmente vítima do acidente. Ele estava
  envolvido.

## 13. O final (indeciso)

Ideia forte: o jogador chega ao sistema central. LIA pergunta: *"Which
instance should be preserved?"* E aparece: CURRENT INSTANCE / ECHO 01 /
ECHO 02 / ECHO 03. Aquilo que era apenas mecânica de puzzle vira questão
narrativa — porque os echoes passaram o jogo inteiro sendo tratados como
cópias. Mas talvez não sejam.

## 14. Visual

Muda a direção do slice: não precisamos de gráficos absurdos, precisamos
de **identidade**. Pixel art sci-fi industrial — entre estação científica,
laboratório abandonado, infraestrutura pesada: computadores CRT, cabos,
painéis, iluminação de emergência, vapor, partículas, sinais de desgaste.
E principalmente: a estação precisa parecer **habitada anteriormente**.
Não pode parecer um mapa feito para o jogador. Tem que parecer que pessoas
trabalhavam ali.

## 15. Som

Ventilação, máquinas, relés, alarmes distantes, passos, portas
pneumáticas, eletricidade, rádio, ruído temporal, silêncio. E quando
aparece um echo: um som muito característico — o jogador ouve antes de
necessariamente vê-lo.

## 16. A regra de escopo continua

Não transformar num jogo gigantesco: **pequeno em tamanho, grande em
densidade**. 8 salas podem parecer um mundo inteiro se cada área tiver
história, função, personagens, segredos, conexões, mudanças temporais,
exploração.

**Direção final:** NULL//SHIFT é uma aventura narrativa sci-fi de
exploração e sobrevivência em uma estação de pesquisa temporal onde o
jogador utiliza versões anteriores de si mesmo para atravessar um ambiente
que parece estar preso entre diferentes estados da realidade. E a mecânica
continua sendo o coração. Só que agora ela serve ao mundo.

---

---

# REVIEW — Muse (2026-10-02)

## Veredito geral

**APROVO a direção, com três objeções arquiteturais sérias e uma objeção
de escopo.** Nada aqui mata o projeto. Mas dois pontos (§7–§8 e §10)
contradizem decisões locked e precisam de decision records novos antes de
qualquer implementação — e o escopo real desta bíblia não cabe num fim de
semana. Detalhes abaixo.

## O que eu aprovo sem ressalvas

1. **A fantasia do técnico comum.** "Eu preciso trabalhar junto comigo
   mesmo" é mais específica e mais forte que "coopere com seu passado".
   Elias Voss como não-especialista justifica o jogador descobrir junto —
   isso é design narrativo correto, não flavor.
2. **LIA como IA inconsistente, não maligna.** "Bom retorno, Elias" na
   primeira visita é horror barato de produzir (uma string condicional) e
   caríssimo em efeito. Aprovadíssimo.
3. **Storytelling ambiental da §11.** STAFF COUNT: 14 → CURRENT STAFF: 0
   custa zero código e entrega mais que cutscene. É exatamente a filosofia
   "pequeno em tamanho, grande em densidade".
4. **"Por que existe um limite?" (§9).** Transformar D005 (cap de 3
   echoes, decisão técnica) em questão narrativa é o tipo de coisa que
   separa jogo com identidade de jogo com mecânica. De graça.
5. **O final (§13).** A escolha da instância weaponiza a mecânica contra o
   jogador. É o tipo de final que só este jogo pode ter. Não decidir ainda
   está correto.
6. **O mapa da estação (§7).** Hub + spokes: 8 áreas interconectadas dão
   sensação de mundo com o room budget que já temos (piso de 8 salas).
   Backtracking com propósito é o multiplicador de densidade mais barato
   que existe — *se* a arquitetura suportar (ver objeção 1).

## Objeção 1 — Backtracking vs. modelo de reset (ARQUITETURAL, séria)

**Conflito real.** Hoje está locked: transições de sala **apagam echoes**,
snapshots são **por sala**, e nada persiste entre ciclos exceto
recordings/unlocks/stats (D006, §4/§6 de ARCHITECTURE, teste T8). A bíblia
quer: voltar a áreas anteriores e encontrar a estação **mudada** — portas
abertas que continuam abertas, máquinas consertadas, áreas que reagem à
fase temporal.

Isso exige no mínimo:
- **D016 — modelo de mundo persistente:** deltas por sala (portas/flags)
  que sobrevivem a transições e resets, separados do snapshot de ciclo.
- **D017 — categoria TEMPORAL:** a §8 da bíblia nomeia exatamente o que
  falta na nossa classificação RESETTABLE/PERSISTENT/SESSION/DERIVED —
  estado que depende da fase temporal (ex.: máquina operável só quando um
  echo a "segura no passado").

Não é rejeição: é o próximo trabalho de design. Mas T8 e partes de T6
teriam que ser reescritos, e o modelo de snapshot atual não cobre isso.
**Nada de backtracking persistente antes de D016/D017 existirem.**

Nota de custo: dá para baratear. "A estação mudou" pode ser 80% cosmético
e scriptado (luzes, sons, terminais com texto novo por contador de
visitas) e 20% real (flags de porta/energia). Recomendo essa divisão.

## Objeção 2 — Echoes rogues vs. determinismo (ARQUITETURAL, séria)

**Conflito real.** O §10 é ótimo horror — mas se um echo puder agir além
da sua gravação, o determinismo que torna os puzzles justos e testáveis
(D004, T4, T7) quebra. Um sistema onde "às vezes o replay mente" não tem
como ser QA-ado.

**Solução proposta (D018):** echoes rogues **não são recordings do
jogador** — são entidades scriptadas vestindo o visual do echo. O modelo
do jogador continua determinístico e sagrado; o horror vive numa camada
separada, com regras próprias e explícitas (quando aparece, o que faz,
como termina). O jogador nunca precisa saber a diferença — mas o design
precisa. Se a bíblia for adotada, o §10 vira: "entidades eco-like
scriptadas", nunca "recordings que desobedecem".

## Objeção 3 — Escopo: isto não é mais um jogo de fim de semana (honesta)

4 atos, 3 personagens com arco, backtracking, beats de horror, LIA com
falas condicionais — isso é um projeto de **2 a 4 semanas** neste nível de
densidade, não um fim de semana. As opções honestas:

- **(a)** v1.0 = Atos I–II (Wake + Power), que é essencialmente o slice
  atual expandido para o piso de 8 salas. Atos III–IV viram roadmap
  pós-launch. O slice continua válido como fundação.
- **(b)** Redefinir "fim de semana" para "o tempo que levar" e tratar o
  projeto como o jogo principal do portfólio.

Recomendo (a): ela preserva tudo que foi validado e não joga fora o Gate 4.
A bíblia continua sendo o norte — só o cronograma muda.

## Objeção 4 — Diálogo: manter o bound (menor)

Elias fala, LIA fala — ótimo, mas o escopo locked diz: sem dialogue trees,
terminais com ≤3 linhas, nada que bloqueie progresso. Proponho o bound
explícito: **falas são barks de terminal/cartão, nunca árvores, nunca
bloqueantes, nunca obrigatórias para resolver puzzles.** Se um dia virar
sistema de diálogo, vira decision record novo.

## O que eu mudaria na v0.1

1. **§8, exemplo da máquina:** hoje está vago ("o presente interage com o
   estado deixado pelo passado"). Para virar design, precisa responder:
   o estado deixado pelo echo é PERSISTENT (fica para sempre) ou TEMPORAL
   (vale enquanto o ciclo dura)? Cada resposta gera puzzles diferentes.
   Deixar para D017.
2. **§12, Ato II "primeiro NPC através de comunicação":** cuidado para
   Tomas não virar tutorial falante. Ele funciona melhor como voz
   assíncrona (mensagens encontradas, nunca em tempo real) — preserva
   solidão, que é o tema.
3. **Falta um bound de texto.** Proponho: total de palavras de narrativa
   < 1500 na v1.0 (hoje o bound é 600; a bíblia justifica aumentar, mas
   com teto).

## Conflitos mapeados com decisões locked

| Bíblia | Decisão locked | Situação |
|---|---|---|
| §7 backtracking / §8 TEMPORAL | D006, ARCH §4/§6, T8 | CONFLITO — exige D016/D017 |
| §10 rogue echo | D004 (determinismo) | CONFLITO — exige D018 (rogue = scriptado) |
| §5–6, §11–13 personagens/texto | scope §6 (≤600 palavras, sem trees) | COMPATÍVEL com bound ampliado |
| §7 mapa hub+spokes | room budget 8–12 | COMPATÍVEL |
| §9 "por que o limite?" | D005 | COMPATÍVEL (de graça) |
| §14–15 visual/som | placeholder-first | COMPATÍVEL (direção, não escopo) |
| §16 densidade > tamanho | filosofia do projeto | COMPATÍVEL (é a mesma regra) |

## Próximos passos propostos

1. Lucas decide: **adotar** a v0.1 como direção oficial ou manter como
   referência.
2. Se adotar: eu redijo D016 (mundo persistente), D017 (categoria
   TEMPORAL), D018 (rogue = scriptado) e o delta de arquitetura para o
   Gate 5 — **sem implementar nada**.
3. Independente da decisão: o playtest do slice (protocolo pronto)
   continua valendo — compreensão da mecânica não depende da bíblia.
4. Recomendação de cronograma: v1.0 = Atos I–II (opção a da Objeção 3).
