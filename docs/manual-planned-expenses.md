# Gastos planificados manuales

## Objetivo

Permitir que Alejandro añada gastos fijos o previsibles que no siempre aparecen como transacción bancaria o de tarjeta.

Ejemplos:
- peluquería
- clases
- efectivo
- pago a un amigo
- cuota informal
- mantenimiento pagado en mano

## Qué debe permitir el sistema

- crear un gasto planificado manual
- marcarlo como recurrente o puntual
- asignarle importe esperado
- asignarle fecha o patrón de repetición
- mostrarlo en el calendario financiero junto a pagos detectados automáticamente
- marcarlo como pagado, omitido o pendiente

## Tipos

### 1. Planned manual series
Serie manual recurrente.

Ejemplos:
- peluquería cada 3 semanas
- fisioterapia el día 15 aproximado
- cuota de algo no domiciliado

### 2. Planned manual occurrence
Gasto puntual manual.

Ejemplos:
- comprar regalo el día 22
- pago en efectivo el próximo martes

## UX recomendada

- formulario rápido: nombre, importe, fecha/patrón, notas
- posibilidad de vincularlo después a una transacción real si acaba apareciendo en banco o tarjeta
- mostrar si el gasto fue:
  - previsto manual
  - detectado automáticamente
  - confirmado por transacción real

## Reglas de negocio

- un planned manual puede convivir con recurrencias detectadas automáticamente
- si luego aparece una transacción real coincidente, se puede reconciliar
- el calendario debe mezclar:
  - manuales
  - detectados
  - confirmados

## MVP

- tabla `manual_planned_items`
- endpoint CRUD simple
- inclusión en overview y calendario
