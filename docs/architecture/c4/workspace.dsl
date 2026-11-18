workspace "San Camilo en Línea" "Modelo C4 de la plataforma de e-commerce para el Mercado San Camilo de Arequipa (Lab 08)" {

    !identifiers hierarchical

    model {

        // ==========================================
        // 1. PERSONAS
        // ==========================================
        cliente = person "Cliente" "Usuario que busca productos, arma un carrito multi-puesto y realiza pagos con Yape/Plin."
        comerciante = person "Comerciante" "Comerciante del mercado que administra sus productos y atiende pedidos desde su celular."
        repartidor = person "Repartidor" "Personal encargado del recojo de pedidos en los puestos y su entrega final."

        // ==========================================
        // 2. SISTEMA Y CONTENEDORES (Actualizado Lab 08)
        // ==========================================
        sancamilo = softwareSystem "San Camilo en Línea" "Plataforma e-commerce para digitalizar ventas de mercados de Arequipa." {

            pwa = container "Aplicación Web Progresiva (PWA)" "Interfaz web liviana para clientes, comerciantes y repartidores con soporte offline-first." "React + Service Workers" "Web Browser"

            api = container "API Backend" "Monolito modular con circuit breaker, cache y políticas RLS [QA-01, QA-03, QA-04]" "Python / Django REST Framework" {

                // --- Componente 1: Módulo Catálogo ---
                compCatalogo = component "Módulo Catálogo" \
                    "Gestiona el catálogo de productos con cache en memoria y consultas indexadas [QA-01]." \
                    "Django App (catalogo)"

                // --- Componente 2: Módulo Pedidos ---
                compPedidos = component "Módulo Pedidos" \
                    "Coordina el ciclo de vida del pedido multi-puesto y reserva de stock transaccional." \
                    "Django App (pedidos)"

                // --- Componente 3: Módulo Pagos ---
                compPagos = component "Módulo Pagos" \
                    "Procesa pagos integrando Decorator con Circuit Breaker y persistencia en tabla Outbox [QA-03]." \
                    "Django App (pagos)"

                // --- Componente 4: Módulo Notificaciones ---
                compNotificaciones = component "Módulo Notificaciones" \
                    "Encola mensajes de WhatsApp de forma asíncrona mediante el Worker de Tareas." \
                    "Django App (notificaciones) + Celery Task"

                // --- Componente 5: Módulo Entregas ---
                compEntregas = component "Módulo Entregas" \
                    "Gestiona la asignación y seguimiento de repartidores para las entregas multi-puesto." \
                    "Django App (entregas)"

                // --- Relaciones internas entre componentes ---
                compPedidos -> compCatalogo "Consulta stock disponible antes de confirmar" "Python method call"
                compPedidos -> compPagos "Solicita procesamiento de pago protegido por circuit breaker" "Python method call"
                compPedidos -> compNotificaciones "Encola notificación al comerciante tras confirmar" "Python method call"
                compPedidos -> compEntregas "Crea registro de entrega al confirmar pedido" "Python method call"
            }

            db = container "Base de Datos" "Almacena datos transaccionales, tabla outbox y politicas RLS de aislamiento [QA-03, QA-04]" "PostgreSQL 16" "Database"
            worker = container "Worker de Tareas" "Procesa reintentos outbox, notificaciones y sincronizacion [QA-03]" "Celery / Python"
            cola = container "Cola de Tareas y Caché" "Cache Redis con TTL 30s y broker de mensajes [QA-01]" "Redis 7" "Queue"
        }

        // ==========================================
        // 3. SISTEMAS EXTERNOS
        // ==========================================
        pasarela = softwareSystem "Proveedor de Pagos" "Procesa y verifica pagos con Yape y Plin (sujeto a caídas transitorias)." "Externo"
        whatsapp = softwareSystem "WhatsApp Business API" "Envía notificaciones de pedidos a los comerciantes." "Externo"

        // ==========================================
        // 4. RELACIONES NIVEL 1 - CONTEXTO
        // ==========================================
        cliente -> sancamilo "Busca productos, realiza pedidos multi-puesto y paga"
        comerciante -> sancamilo "Administra catálogo, stock y atiende pedidos"
        repartidor -> sancamilo "Consulta entregas asignadas y actualiza estado"
        sancamilo -> pasarela "Verifica pagos mediante pasarela externa" "HTTPS/JSON"
        sancamilo -> whatsapp "Envía notificaciones de nuevos pedidos" "HTTPS/JSON"

        // ==========================================
        // 5. RELACIONES NIVEL 2 - CONTENEDORES
        // ==========================================
        cliente -> sancamilo.pwa "Usa la PWA para comprar" "HTTPS"
        comerciante -> sancamilo.pwa "Usa la PWA para gestionar su puesto" "HTTPS"
        repartidor -> sancamilo.pwa "Usa la PWA para ver entregas" "HTTPS"

        sancamilo.pwa -> sancamilo.api "Realiza peticiones REST" "HTTPS/JSON"
        sancamilo.api -> sancamilo.db "Consulta datos con RLS y persiste transacciones diferidas [QA-03, QA-04]" "SQL/TCP"
        sancamilo.api -> sancamilo.cola "Consulta cache Redis (TTL 30s) y encola eventos [QA-01]" "Redis Protocol"
        sancamilo.worker -> sancamilo.cola "Consume tareas pendientes" "Redis Protocol"
        sancamilo.worker -> sancamilo.db "Procesa y reintenta pagos outbox diferidos [QA-03]" "SQL/TCP"
        sancamilo.worker -> whatsapp "Envía mensajes a comerciantes" "HTTPS/JSON"
        sancamilo.api -> pasarela "Verifica constancias de pago (con timeout y breaker) [QA-03]" "HTTPS/JSON"

        // ==========================================
        // RELACIONES COMPONENTES → INFRAESTRUCTURA
        // ==========================================
        sancamilo.api.compCatalogo -> sancamilo.cola "Consulta y almacena cache de productos (TTL 30s) [QA-01]" "Redis Protocol"
        sancamilo.api.compCatalogo -> sancamilo.db "Consulta productos mediante índices optimizados" "SQL/TCP"
        sancamilo.api.compPedidos -> sancamilo.db "Persiste pedidos globales e ítems aislados por RLS [QA-04]" "SQL/TCP"
        sancamilo.api.compPagos -> sancamilo.db "Guarda pagos en tabla outbox cuando el circuito abre [QA-03]" "SQL/TCP"
        sancamilo.api.compPagos -> pasarela "Llamadas de verificación filtradas por breaker [QA-03]" "HTTPS/JSON"
        sancamilo.api.compEntregas -> sancamilo.db "Registra y actualiza estados de entrega" "SQL/TCP"
        sancamilo.api.compNotificaciones -> sancamilo.cola "Encola mensajes de notificación" "Redis Protocol"
        sancamilo.worker -> sancamilo.cola "Consume tareas de notificación pendientes" "Redis Protocol"

        // Relaciones dinámicas
        sancamilo.pwa -> sancamilo.api.compPedidos "Envía solicitud de confirmación de pedido con referencia Yape" "HTTPS/JSON"
        sancamilo.api.compPedidos -> sancamilo.pwa "Retorna resultado de la confirmación del pedido" "HTTPS/JSON"

        // ==========================================
        // 6. ENTORNO DE DESPLIEGUE: PRODUCCIÓN (VPS)
        // ==========================================
        deploymentEnvironment "Producción" {

            deploymentNode "Dispositivos de Usuario" "Dispositivos móviles y navegadores." "Android / iOS / Desktop" {
                deploymentNode "Navegador Web" "Entorno del cliente." "Chrome / Firefox / Safari" {
                    pwaInstance = containerInstance sancamilo.pwa
                }
            }

            deploymentNode "Servidor en la Nube (VPS)" "VPS de bajo costo que aloja la infraestructura." "Ubuntu 22.04 LTS" {

                deploymentNode "Proxy Inverso" "Termina TLS y sirve activos estáticos." "Nginx 1.25" {
                }

                deploymentNode "Docker Compose" "Orquestador de contenedores para producción." "Docker Compose v2" {

                    deploymentNode "Contenedor API" "Instancia del monolito con reglas RLS y Circuit Breaker." "Docker / Python 3.11" {
                        apiInstance = containerInstance sancamilo.api
                    }

                    deploymentNode "Contenedor Worker" "Worker Celery para outbox y colas asíncronas." "Docker / Python 3.11" {
                        workerInstance = containerInstance sancamilo.worker
                    }

                    deploymentNode "Contenedor Redis" "Caché de catálogo y broker de mensajes." "Docker / Redis 7" {
                        colaInstance = containerInstance sancamilo.cola
                    }

                    deploymentNode "Contenedor PostgreSQL" "Base de datos con tabla outbox y políticas RLS." "Docker / PostgreSQL 16" {
                        dbInstance = containerInstance sancamilo.db
                    }
                }
            }

            deploymentNode "Servicios Externos" "SaaS externos fuera del control del equipo." "Internet / Cloud" {
                deploymentNode "Proveedor Yape/Plin" "API HTTPS para pagos." "HTTPS/REST" {
                    pasarelaInstance = softwareSystemInstance pasarela
                }
                deploymentNode "Meta Cloud" "WhatsApp Business API." "HTTPS/REST" {
                    whatsappInstance = softwareSystemInstance whatsapp
                }
            }
        }
    }

    // ==========================================
    // 7. VISTAS DEL MODELO
    // ==========================================
    views {

        systemContext sancamilo "Contexto" "Nivel 1: Contexto del sistema San Camilo en Línea." {
            include *
            autolayout lr
        }

        container sancamilo "Contenedores" "Nivel 2: Diagrama de contenedores con tácticas de resiliencia y caché [QA-01, QA-03, QA-04]." {
            include *
            autolayout lr
        }

        component sancamilo.api "Componentes" "Nivel 3: Componentes del API con Circuit Breaker y Outbox integrado." {
            include *
            autolayout lr
        }

        dynamic sancamilo.api "ConfirmacionPago" "Flujo de confirmación con resiliencia de pagos diferidos." {
            title "Confirmación y Pago de Pedido Multi-Puesto (Resiliencia QA-03)"

            sancamilo.pwa -> sancamilo.api.compPedidos "1. POST /pedidos/confirmar (referenciaYape)"
            sancamilo.api.compPedidos -> sancamilo.api.compPagos "2. procesarPagoYape(pedidoId, referenciaYape)"
            sancamilo.api.compPagos -> pasarela "3. verificarPago(montoTotal, referenciaYape)"
            sancamilo.api.compPedidos -> sancamilo.db "4. guardar(pedidoGlobal) – estado PAGADO o PENDIENTE_OUTBOX"
            sancamilo.api.compPedidos -> sancamilo.api.compNotificaciones "5. notificarNuevoPedidoComerciante(puesto, pedidoPuesto)"
            sancamilo.api.compNotificaciones -> sancamilo.cola "6. enqueue(mensajeWhatsApp) – asíncrono"
            sancamilo.api.compPedidos -> sancamilo.pwa "7. 200 OK – estado de la transacción"

            autolayout lr
        }

        deployment sancamilo "Producción" "Despliegue-Produccion" "Vista de despliegue en VPS único mediante Docker Compose." {
            include *
            autolayout lr
        }

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
