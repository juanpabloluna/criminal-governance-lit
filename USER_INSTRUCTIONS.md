# Using the Criminal Governance Literature Expert

*Instrucciones en español más abajo.*

## What this app is

A research assistant built on a corpus of 304 academic papers on criminal governance, organized crime, illegal markets, violence, and state capacity, with a Latin American focus. You can search the corpus, ask questions and get citation-backed answers, generate short literature syntheses, and have a draft reviewed against the literature.

## What you need

1. **The app link and the access code**, provided by Juan Pablo Luna.
2. **Your own Anthropic API key** for the Claude-powered features. The app runs Claude queries on your key, so each user pays for their own usage.

Note: a Claude.ai subscription (Free, Pro, or Max) and Claude Code do **not** include an API key. The API key comes from a separate developer account at the Anthropic Console. It takes about five minutes to set up.

## Getting your API key (one time)

1. Go to **console.anthropic.com** and create an account (any email works; you can use the same email as your Claude.ai account, but the billing is separate).
2. In the Console, open **Billing** and add credits. US$5 is plenty to start; typical queries in this app cost a few cents each.
3. Open **API Keys**, click **Create Key**, give it a name (for example `lit-expert`), and copy the key. It starts with `sk-ant-`. Store it somewhere safe (a password manager is ideal); the Console will not show it again.

## Using the app

1. Open the app link. Enter **your name** and the **access code** you were given, then click Enter. Please use your real name; queries are logged by name so the tool can be improved.
2. Open any Claude-powered page (Question Answering, Agentic Q&A, Literature Synthesis, or Research Review). Paste your API key into the **sidebar field on the left** and press Enter.
3. Ask away. Answers cite specific papers from the corpus.

You need to re-enter the key each time you open the app in a new browser session. It is kept only in your browser session and never stored on the server.

**No key? You can still use the corpus.** The search and bibliography pages run entirely on the app's local index and require no API key at all.

## The pages

- **Question Answering**: ask a question, get an answer with citations to specific papers, filtered by collection or year if you wish.
- **Agentic Q&A**: Claude runs its own multi-step search of the corpus before answering. Slower, more thorough, and somewhat more expensive per query.
- **Literature Synthesis**: give a topic, get a short structured literature review drawn from the corpus.
- **Research Review**: paste a draft passage and get feedback on how it relates to the literature, including supporting and contradicting work.
- **Bibliography / Search**: browse and search the corpus directly. No API key needed.

## Costs and limits

- Usage is billed to your own Anthropic account at standard API rates. A typical question costs on the order of a few cents; synthesis and agentic queries cost more because they process more text.
- You can check your spending anytime in the Console under **Usage**.
- If a query fails with an authentication error, the key was mistyped or revoked; create a fresh one in the Console. If it fails with a credit error, add credits under Billing.

## Privacy

- Your API key is never logged or stored on the server.
- Queries (your name, the page used, and the query text) are logged so the maintainer can understand usage patterns and improve the tool.
- The corpus was last updated in January 2026; papers published after that date are not included. Answers describe what is in the corpus, which is not an exhaustive bibliography of the field.

---

# Instrucciones en español

## Qué es esta aplicación

Un asistente de investigación construido sobre un corpus de 304 artículos académicos sobre gobernanza criminal, crimen organizado, mercados ilegales, violencia y capacidad estatal, con foco en América Latina. Permite buscar en el corpus, hacer preguntas con respuestas respaldadas por citas, generar síntesis breves de literatura y revisar borradores contra la literatura.

## Qué necesitas

1. **El enlace de la aplicación y el código de acceso**, provistos por Juan Pablo Luna.
2. **Tu propia clave API de Anthropic** para las funciones que usan Claude. La aplicación ejecuta las consultas con tu clave, de modo que cada persona paga su propio uso.

Nota: una suscripción a Claude.ai (Free, Pro o Max) y Claude Code **no** incluyen clave API. La clave se obtiene en una cuenta de desarrollador separada, en la Consola de Anthropic. Crearla toma unos cinco minutos.

## Obtener tu clave API (una sola vez)

1. Entra a **console.anthropic.com** y crea una cuenta (sirve cualquier correo; puede ser el mismo de tu cuenta Claude.ai, pero la facturación es aparte).
2. En la Consola, abre **Billing** y carga créditos. Con US$5 alcanza de sobra para empezar; una consulta típica cuesta unos pocos centavos.
3. Abre **API Keys**, haz clic en **Create Key**, ponle un nombre (por ejemplo `lit-expert`) y copia la clave. Empieza con `sk-ant-`. Guárdala en un lugar seguro (idealmente un gestor de contraseñas); la Consola no la mostrará de nuevo.

## Usar la aplicación

1. Abre el enlace. Escribe **tu nombre** y el **código de acceso** que recibiste, y haz clic en Enter. Usa tu nombre real, por favor; las consultas se registran por nombre para poder mejorar la herramienta.
2. Abre cualquier página con funciones de Claude (Question Answering, Agentic Q&A, Literature Synthesis o Research Review). Pega tu clave API en el **campo de la barra lateral izquierda** y presiona Enter.
3. Consulta con libertad. Las respuestas citan artículos específicos del corpus.

Tendrás que volver a ingresar la clave cada vez que abras la aplicación en una nueva sesión del navegador. La clave se mantiene solo en tu sesión y nunca se guarda en el servidor.

**¿Sin clave? Igual puedes usar el corpus.** Las páginas de búsqueda y bibliografía funcionan por completo con el índice local de la aplicación y no requieren clave API.

## Las páginas

- **Question Answering**: haces una pregunta y recibes una respuesta con citas a artículos específicos, con filtros por colección o año si lo deseas.
- **Agentic Q&A**: Claude ejecuta su propia búsqueda de varios pasos en el corpus antes de responder. Más lento, más exhaustivo y algo más caro por consulta.
- **Literature Synthesis**: das un tema y recibes una revisión de literatura breve y estructurada, basada en el corpus.
- **Research Review**: pegas un pasaje de borrador y recibes comentarios sobre cómo se relaciona con la literatura, incluyendo trabajos que lo apoyan y lo contradicen.
- **Bibliography / Search**: navega y busca directamente en el corpus. No requiere clave API.

## Costos y límites

- El uso se factura a tu propia cuenta de Anthropic a tarifas estándar de API. Una pregunta típica cuesta del orden de unos pocos centavos; las síntesis y las consultas agénticas cuestan más porque procesan más texto.
- Puedes revisar tu gasto en la Consola, sección **Usage**.
- Si una consulta falla con error de autenticación, la clave está mal copiada o fue revocada; crea una nueva en la Consola. Si falla por falta de créditos, carga saldo en Billing.

## Privacidad

- Tu clave API nunca se registra ni se guarda en el servidor.
- Las consultas (tu nombre, la página usada y el texto de la consulta) quedan registradas para que el responsable pueda entender los patrones de uso y mejorar la herramienta.
- El corpus se actualizó por última vez en enero de 2026; los trabajos publicados después de esa fecha no están incluidos. Las respuestas describen lo que hay en el corpus, que no es una bibliografía exhaustiva del campo.
