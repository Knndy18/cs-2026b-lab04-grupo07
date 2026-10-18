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
                // [ESPACIO PARA EL ENCARGADO DE E3]: Agrega aquí tus 4+ componentes
                // Ejemplo:
                // catalogo = component "Módulo Catálogo" "Gestiona productos y stock." "Django App"
                // pedidos = component "Módulo Pedidos" "Gestiona pedidos multi-puesto." "Django App"
                // =======================================================================
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
    }

    // ==========================================
    // 6. VISTAS DEL MODELO (E1 & E2)
    // ==========================================
    views {
        
        systemContext sancamilo "Contexto" "Nivel 1: Contexto del sistema San Camilo en Línea y su entorno." {
            include *
            autolayout lr
        }

        container sancamilo "Contenedores" "Nivel 2: Diagrama de contenedores del Monolito Modular San Camilo en Línea." {
            include *
            autolayout lr
        }

        // Configuración de estilos visuales
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
