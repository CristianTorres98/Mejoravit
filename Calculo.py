#Calculo de comision del 22%
def comision(prestamo):
    porcentaje = (prestamo / 100) * 22
    print(f'Comision (22%): -${porcentaje:.2f}')
    return porcentaje
  
#Descuento de la comision
def descuento_comision(credito,comision):
    sub_total = credito - comision
    print(f'Sub Total: ${sub_total:.2f}')
    return sub_total
    
#Calculo de desucento del contrato
def comision_tramite(subtotal):
    total = subtotal - 6000
    print(f'Gastos de contrato: -$6000.00')
    print(f'Total libre: ${total:.2f}')
    return total


