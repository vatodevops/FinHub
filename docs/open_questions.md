# Preguntas abiertas

## Bancos / agregación
- ¿GoCardless B.A.D. cubre bien BBVA, Ibercaja, ING, Sabadell y Revolut en este caso?
- ¿Conviene usar un único agregador o dejar proveedor abstracto desde el principio?

## Curve
- ¿La fuente de Curve será API/export o ingestión indirecta?
- ¿Qué patrones exactos aparecen en BBVA, Ibercaja, ING, Sabadell y Revolut cuando el cargo viene de Curve?
- ¿Cómo modelar `Go Back in Time`?

## Inversiones
- ¿Qué proveedores tienen API usable de verdad?
- ¿Qué se considera suficiente en fase 2: valor de cartera, posiciones o también rentabilidad?

## Seguridad
- ¿auth local con password + TOTP desde el inicio o más simple para MVP?
- ¿cómo guardar tokens/cookies/credenciales de conectores?

## Reporting
- ¿las transferencias internas entre cuentas se quieren ocultar por defecto en el cashflow?
- ¿cuánta granularidad mensual/categorías quieres en la UI final?
