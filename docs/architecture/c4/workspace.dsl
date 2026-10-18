workspace "San Camilo en Línea" "Modelo C4 de la plataforma de e-commerce para el Mercado San Camilo de Arequipa" {

    !identifiers hierarchical

    model {

        // ==========================================
        // 1. PERSONAS (E1)
        // ==========================================
        cliente = person "Cliente" "Usuario que busca productos, arma un carrito multi-puesto y realiza pagos con Yape."
        comerciante = person "Comerciante" "Comerciante del mercado que administra sus productos y atiende pedidos desde su celular."
        repartidor = person "Repartidor" "Personal encargado del recojo de pedidos en los puestos y su entrega final."

        // ==========================================
        // 2. SISTEMA Y CONTENEDORES (E1 & E2)
        // ==========================================
        sancamilo = softwareSystem "San Camilo en Línea" "Plataforma e-commerce MVP para digitalizar las ventas del Mercado San Camilo." {

            pwa = container "Aplicación Web Progresiva (PWA)" "Interfaz web liviana para clientes, comerciantes y repartidores." "React + Service Workers" "Web Browser"

            api = container "API Backend" "Monolito modular que implementa los casos de uso del catálogo, pedidos y pagos." "Python / Django REST Framework" {

                // =======================================================================
                // E3 – NIVEL 3: COMPONENTES DEL API BACKEND
                // Mapeados desde docs/design/paquetes.puml (ADR-001: Monolito Modular)
                // Grafo estrictamente acíclico: catalogo ← pedidos → pagos → notificaciones
                // =======================================================================

                // --- Componente 1: Módulo Catálogo ---
                // Origen: package "catalogo" en paquetes.puml (ServicioCatalogo, Producto, Puesto)
                compCatalogo = component "Módulo Catálogo" \
                    "Gestiona el catálogo de productos agrupados por puesto. Expone endpoints de consulta, filtrado y administración de stock (RF-01, RF-02, RF-05). Implementa el puerto RepositorioCatalogo." \
                    "Django App (catalogo)"

                // --- Componente 2: Módulo Pedidos ---
                // Origen: package "pedidos" en paquetes.puml (ServicioPedidos, PedidoGlobal, PedidoPuesto, ItemPedido)
                compPedidos = component "Módulo Pedidos" \
                    "Propietario del ciclo de vida del pedido multi-puesto. Coordina la confirmación, reserva de stock y cambio de estados de cada PedidoPuesto (RF-03, RF-06, RF-07, R-07)." \
                    "Django App (pedidos)"

                // --- Componente 3: Módulo Pagos ---
                // Origen: package "pagos" en paquetes.puml (ServicioPagos, Pago, PasarelaPago<<port>>)
                compPagos = component "Módulo Pagos" \
                    "Recibe la referencia Yape del cliente, delega la verificación a la pasarela externa mediante el puerto PasarelaPago y devuelve el resultado al módulo de pedidos (RF-04, R-05)." \
                    "Django App (pagos)"

                // --- Componente 4: Módulo Notificaciones ---
                // Origen: package "notificaciones" en paquetes.puml (ServicioNotificaciones, NotificadorWhatsApp<<port>>, ColaMensajes)
                compNotificaciones = component "Módulo Notificaciones" \
                    "Encola mensajes de WhatsApp de forma asíncrona para evitar bloquear la respuesta HTTP al cliente. Gestiona reintentos mediante el Worker de Tareas (RF-08, QA-02)." \
                    "Django App (notificaciones) + Celery Task"

                // --- Componente 5: Módulo Entregas ---
                // Origen: package "entregas" en paquetes.puml (ServicioEntregas, Entrega, RepositorioEntregas<<port>>)
                compEntregas = component "Módulo Entregas" \
                    "Gestiona la asignación de pedidos a repartidores y el seguimiento de estados (recogido, en camino, entregado). Expone endpoints para el actor Repartidor (RF-07, R-06)." \
                    "Django App (entregas)"

                // =======================================================================
                // RELACIONES INTERNAS ENTRE COMPONENTES (sin ciclos)
                // Sentido: API → módulos de dominio; Pedidos orquesta → Catálogo, Pagos, Notificaciones
                // =======================================================================
                compPedidos -> compCatalogo "Consulta stock disponible antes de confirmar" "Python method call"
                compPedidos -> compPagos "Solicita verificación de referencia Yape" "Python method call"
                compPedidos -> compNotificaciones "Encola notificación al comerciante tras confirmar" "Python method call"
                compPedidos -> compEntregas "Crea registro de entrega al confirmar pedido con delivery" "Python method call"
            }

            db = container "Base de Datos" "Almacena usuarios, productos, carritos, pedidos e historial de auditoría." "PostgreSQL 16" "Database"
            worker = container "Worker de Tareas" "Ejecuta notificaciones por WhatsApp y reintentos en segundo plano." "Celery"
            cola = container "Cola de Tareas y Caché" "Gestión de colas de trabajo asíncronas y almacenamiento en caché del catálogo." "Redis 7" "Queue"
        }

        // ==========================================
        // 3. SISTEMAS EXTERNOS (E1)
        // ==========================================
        pasarela = softwareSystem "Proveedor de Pagos" "Procesa y verifica las referencias de pagos con Yape y Plin." "Externo"
        whatsapp = softwareSystem "WhatsApp Business API" "Envía notificaciones de pedidos a los comerciantes." "Externo"

        // ==========================================
        // 4. RELACIONES NIVEL 1 - CONTEXTO (E1)
        // ==========================================
        cliente -> sancamilo "Busca productos, realiza pedidos multi-puesto y paga"
        comerciante -> sancamilo "Administra catálogo, stock y acepta pedidos"
        repartidor -> sancamilo "Consulta entregas asignadas y actualiza estado"
        sancamilo -> pasarela "Verifica referencias de pago Yape/Plin" "HTTPS/JSON"
        sancamilo -> whatsapp "Envía notificaciones de nuevos pedidos" "HTTPS/JSON"

        // ==========================================
        // 5. RELACIONES NIVEL 2 - CONTENEDORES (E2)
        // ==========================================
        cliente -> sancamilo.pwa "Usa la PWA para comprar" "HTTPS"
        comerciante -> sancamilo.pwa "Usa la PWA para gestionar su puesto" "HTTPS"
        repartidor -> sancamilo.pwa "Usa la PWA para ver entregas" "HTTPS"

        sancamilo.pwa -> sancamilo.api "Realiza peticiones REST" "HTTPS/JSON"
        sancamilo.api -> sancamilo.db "Lee y escribe datos transaccionales" "SQL/TCP"
        sancamilo.api -> sancamilo.cola "Encola tareas de notificación y lee caché" "Redis Protocol"
        sancamilo.worker -> sancamilo.cola "Consume tareas pendientes" "Redis Protocol"
        sancamilo.worker -> whatsapp "Envía mensajes a comerciantes" "HTTPS/JSON"
        sancamilo.api -> pasarela "Verifica constancias de pago" "HTTPS/JSON"

        // ==========================================
        // RELACIONES COMPONENTES → INFRAESTRUCTURA (E3)
        // ==========================================
        sancamilo.api.compCatalogo -> sancamilo.db "Lee y escribe productos y stock" "SQL/TCP"
        sancamilo.api.compPedidos -> sancamilo.db "Persiste pedidos globales, por puesto e ítems" "SQL/TCP"
        sancamilo.api.compPagos -> sancamilo.db "Registra comprobantes y estado de pago" "SQL/TCP"
        sancamilo.api.compEntregas -> sancamilo.db "Registra y actualiza estados de entrega" "SQL/TCP"
        sancamilo.api.compNotificaciones -> sancamilo.cola "Encola mensajes de WhatsApp de forma asíncrona" "Redis Protocol"
        sancamilo.api.compPagos -> pasarela "Verifica referencia Yape mediante YapeAdapter" "HTTPS/JSON"
        sancamilo.worker -> sancamilo.cola "Consume tareas de notificación pendientes" "Redis Protocol"

        // --- Relaciones explícitas requeridas por la vista dynamic (E4) ---
        // Structurizr solo permite en dynamic relaciones declaradas en el modelo.
        sancamilo.pwa -> sancamilo.api.compPedidos "Envía solicitud de confirmación de pedido con referencia Yape" "HTTPS/JSON"
        sancamilo.api.compPedidos -> sancamilo.pwa "Retorna resultado de la confirmación del pedido" "HTTPS/JSON"

        // ==========================================
        // E5 – ENTORNO DE DESPLIEGUE: PRODUCCIÓN
        // Coherente con despliegue.puml y drivers.md (R-01, R-02, R-03)
        // ==========================================
        deploymentEnvironment "Producción" {

            // --- Nivel 1: Dispositivos de usuario ---
            deploymentNode "Dispositivos de Usuario" "Smartphones, tablets y PCs de clientes, comerciantes y repartidores." "Android / iOS / Desktop" {
                deploymentNode "Navegador Web" "Entorno de ejecución del cliente web." "Chrome / Firefox / Safari" {
                    pwaInstance = containerInstance sancamilo.pwa
                }
            }

            // --- Nivel 2: Servidor en la Nube (VPS único – R-03) ---
            deploymentNode "Servidor en la Nube (VPS)" "Servidor virtual privado de bajo costo que aloja toda la plataforma backend." "Ubuntu 22.04 LTS" {

                // Proxy inverso – termina TLS y enruta tráfico HTTP/HTTPS
                deploymentNode "Proxy Inverso" "Termina TLS, sirve activos estáticos de la PWA y enruta al backend." "Nginx 1.25" {
                    // El proxy enruta a la API; no hay containerInstance de PWA aquí
                    // ya que la PWA se ejecuta en el navegador del usuario.
                }

                // Entorno Docker Compose – contiene todos los contenedores de backend
                deploymentNode "Docker Compose" "Orquestador local de contenedores para el entorno de producción MVP." "Docker Compose v2" {

                    deploymentNode "Contenedor API" "Instancia del monolito modular Django." "Docker / Python 3.11" {
                        apiInstance = containerInstance sancamilo.api
                    }

                    deploymentNode "Contenedor Worker" "Instancia del worker Celery para tareas asíncronas." "Docker / Python 3.11" {
                        workerInstance = containerInstance sancamilo.worker
                    }

                    deploymentNode "Contenedor Redis" "Instancia de Redis para cola de tareas y caché del catálogo." "Docker / Redis 7" {
                        colaInstance = containerInstance sancamilo.cola
                    }

                    deploymentNode "Contenedor PostgreSQL" "Instancia de la base de datos relacional principal." "Docker / PostgreSQL 16" {
                        dbInstance = containerInstance sancamilo.db
                    }
                }
            }

            // --- Nivel 3: Servicios externos en la nube ---
            deploymentNode "Servicios Externos" "Proveedores SaaS fuera del control del equipo." "Internet / Cloud" {
                deploymentNode "Proveedor Yape/Plin" "API HTTPS para verificación de referencias de pago." "HTTPS/REST" {
                    pasarelaInstance = softwareSystemInstance pasarela
                }
                deploymentNode "Meta Cloud" "Infraestructura de WhatsApp Business API." "HTTPS/REST" {
                    whatsappInstance = softwareSystemInstance whatsapp
                }
            }
        }
    }

    // ==========================================
    // 6. VISTAS DEL MODELO (E1, E2, E3, E4 y E5)
    // ==========================================
    views {

        // --- Vista Nivel 1: Contexto del Sistema (E1) ---
        systemContext sancamilo "Contexto" "Nivel 1: Contexto del sistema San Camilo en Línea y su entorno." {
            include *
            autolayout lr
        }

        // --- Vista Nivel 2: Contenedores (E2) ---
        container sancamilo "Contenedores" "Nivel 2: Diagrama de contenedores del Monolito Modular San Camilo en Línea." {
            include *
            autolayout lr
        }

        // --- Vista Nivel 3: Componentes del API Backend (E3) ---
        component sancamilo.api "Componentes" "Nivel 3: Componentes internos del API Backend. Mapeados desde paquetes.puml (ADR-001: Monolito Modular). El grafo de dependencias es estrictamente acíclico." {
            include *
            autolayout lr
        }

        // --- Vista Dinámica: Flujo de Confirmación y Pago (E4) ---
        // Flujo crítico: "Confirmación y pago de un pedido multi-puesto en San Camilo"
        // Basado estrictamente en docs/design/secuencia-flujo.puml
        dynamic sancamilo.api "ConfirmacionPago" "E4 – Flujo dinámico de confirmación y pago de un pedido multi-puesto con Yape." {
            title "Confirmación y Pago de Pedido Multi-Puesto (Flujo Feliz)"

            sancamilo.pwa -> sancamilo.api.compPedidos "1. POST /pedidos/confirmar (referenciaYape)"
            sancamilo.api.compPedidos -> sancamilo.api.compPagos "2. procesarPagoYape(pedidoId, referenciaYape)"
            sancamilo.api.compPagos -> pasarela "3. verificarPago(montoTotal, referenciaYape)"
            sancamilo.api.compPedidos -> sancamilo.db "4. guardar(pedidoGlobal) – estado PAGADO"
            sancamilo.api.compPedidos -> sancamilo.api.compNotificaciones "5. notificarNuevoPedidoComerciante(puesto, pedidoPuesto)"
            sancamilo.api.compNotificaciones -> sancamilo.cola "6. enqueue(mensajeWhatsApp) – asíncrono"
            sancamilo.api.compPedidos -> sancamilo.pwa "7. 200 OK – resumen del pedido confirmado por puesto"

            autolayout lr
        }

        // --- Vista de Despliegue: Producción (E5) ---
        deployment sancamilo "Producción" "Despliegue-Produccion" "E5 – Vista de despliegue del entorno de producción. Un VPS con Docker Compose (R-03). Coherente con despliegue.puml y drivers.md." {
            include *
            autolayout lr
        }

        // ==========================================
        // Configuración de estilos visuales
        // ==========================================
        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBD9
                color #000000
            }
            element "Database" {
                shape cylinder
            }
            element "Queue" {
                shape pipe
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}
