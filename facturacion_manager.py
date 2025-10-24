from PySide6.QtCore import QObject, Signal, Slot, QThread
from datetime import date, datetime
from zeep import Client
from escpos.printer import Usb
from pdf417gen import encode, render_image
from PIL import Image
import base64
import xml.etree.ElementTree as ET
import os
import json
import traceback
import time
from logger_config import setup_logger

logger = setup_logger()


class FacturacionManager(QObject):
    """Clase que gestiona la generación y la impresión de boletas usando facturacion.cl

    Uso general:
        - Instanciar la clase en el hilo de la GUI o moverla a un QThread.
        - Conectar sus señales de estado (started, finished, error, printed...).
        - Lanzar la generación/impresión emitendo la señal `generate_and_print`.

    Comportamiento clave implementado:
        - No bloqueante: la lógica de trabajo se ejecuta en el hilo donde viva la instancia. Recomiendo moverla a QThread.
        - Cola local en disco para evitar pérdida de ventas: guarda JSON en `queue_dir` antes de procesar.
        - En caso de fallo de red/servicio SOAP -> imprime un comprobante local (mensaje "No se puede generar boleta").
        - Si la impresora está fuera/dañada -> registra el error, descarta la boleta de la cola para evitar reimpresiones en exceso.
    """

    # Señales que externas pueden escuchar
    started = Signal(dict)            # Emite datos cuando comienza el job
    finished = Signal(dict)           # Emite datos cuando termina (exito o fallo)
    error = Signal(str, dict)         # Mensaje de error y contexto
    printed = Signal(dict)            # Emite cuando la impresión (real o fallback) se realizó
    folio_generated = Signal(str)     # Emite folio si fue generado por el servicio

    # Señal para activar desde otra parte (no retorna valor): pasar dict con keys: monto, cantidad, valor_unitario
    generate_and_print = Signal(dict)

    def __init__(self, queue_dir='/var/boletas_queue', wsdl_url=None, printer_cfg=None, parent=None):
        super().__init__(parent)
        self.queue_dir = queue_dir
        os.makedirs(self.queue_dir, exist_ok=True)

        # WSDL y configuración de impresora (vendor/product ids y endpoints opcionales)
        self.wsdl_url = wsdl_url or 'http://ws.facturacion.cl/WSDS/wsplano.asmx?wsdl'
        self.printer_cfg = printer_cfg or {
            'vendor_id': 0x4b43,
            'product_id': 0x3538,
            'in_ep': 0x82,
            'out_ep': 0x02
        }

        # Conectar la señal a la tarea
        self.generate_and_print.connect(self._on_generate_and_print)

    # ---------------------- Helpers internos ----------------------
    def _save_to_queue(self, payload: dict):
        """Guarda la boleta en disco con un nombre único para asegurar persistencia."""
        fname = os.path.join(self.queue_dir, f"boleta_{int(datetime.now().timestamp()*1000)}.json")
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False)
        logger.info(f"Boleta guardada en cola: {fname}")
        return fname

    def _remove_from_queue(self, path):
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Boleta eliminada de cola: {path}")
        except Exception as e:
            logger.warning(f"No se pudo eliminar archivo de cola {path}: {e}")

    def _base64_login(self):
        return {
            'Usuario': base64.b64encode("TYTSPA".encode()).decode(),
            'Rut': base64.b64encode("1-9".encode()).decode(),#1-9
            'Clave': base64.b64encode("plano91098".encode()).decode(),#plano91098
            'Puerto': base64.b64encode("1".encode()).decode(),
            'IncluyeLink': base64.b64encode("1".encode()).decode()
        }

    def _crear_contenido_plano(self, monto_pagado, cantidad_fichas, valor_unitario):
        # (Se reutiliza la lógica del código original para crear el contenido plano)
        UNITARIO = valor_unitario
        PAGADO = monto_pagado
        CANTIDAD = cantidad_fichas

        datos_boleta = {
            'TipoDTE': 39,
            'Folio': 0,
            'FechaEmision': date.today().isoformat(),
            'IndServicio': 3,
            'IndMntNeto': 0,
            'PeriodoDesde': '',
            'PeriodoHasta': '',
            'FechaVenc': '',
            'RUTCliente': '66666666-6',
            'CodInterno': 'coinMCH1',
            'RSCliente': 'Venta sin nombre',
            'GiroCliente': '',
            'DirCliente': '',
            'ComCliente': '',
            'CiuCliente': '',
            'Email': ''
        }

        sucursal = {"Nombre_sucursal": "AUTOLAVADO V2"}
        totales = {
            'MontoExento': 0,
            'MontoNeto': 0,
            'MontoIva': 0,
            'MontoTotal': PAGADO,
            'IVAPropio': 0,
            'IVATercero': 0,
            'OtrosImpuestos': 0,
            'MontoOtros': 0
        }

        detalle = [{
            'NroLinea': 1,
            'Codigo': 1,
            'Descripcion': 'Fichas de lavado',
            'IndExencion': 0,
            'Cantidad': CANTIDAD,
            'PrecioUnitario': UNITARIO,
            'ValorExento': 0,
            'MontoTotalLinea': PAGADO,
            'TipoItem': 'INT1',
            'UnidadMedida': 'UN',
            'PorcDescuento': (((CANTIDAD*UNITARIO) - PAGADO)/(CANTIDAD*UNITARIO))*100 if CANTIDAD > 0 else 0,
            'ValorDescuento': ((CANTIDAD*UNITARIO) - PAGADO)
        }]

        lines = []
        lines.append("->Boleta<-")
        b = datos_boleta
        cab = ";".join([
            str(b['TipoDTE']),
            str(b['Folio']),
            b['FechaEmision'],
            str(b['IndServicio']),
            str(b['IndMntNeto']),
            b['PeriodoDesde'],
            b['PeriodoHasta'],
            b['FechaVenc'],
            b['RUTCliente'],
            b['CodInterno'],
            b['RSCliente'],
            b['GiroCliente'],
            b['DirCliente'],
            b['ComCliente'],
            b['CiuCliente'],
            b['Email']
        ])+';'
        lines.append(cab)

        lines.append("->BoletaSucursal<-")
        suc = ";".join([sucursal["Nombre_sucursal"]]) + ";"
        lines.append(suc)

        lines.append("->BoletaTotales<-")
        t = totales
        tot = ";".join(str(t[k]) for k in [
            'MontoExento', 'MontoNeto', 'MontoIva', 'MontoTotal',
            'IVAPropio', 'IVATercero', 'OtrosImpuestos', 'MontoOtros'
        ]) + ";"
        lines.append(tot)

        lines.append("->BoletaDetalle<-")
        for item in detalle:
            det = ";".join([
                str(item['NroLinea']),
                str(item['Codigo']),
                str(item['Descripcion']),
                str(item['IndExencion']),
                str(item['Cantidad']),
                str(item['PrecioUnitario']),
                str(item['ValorExento']),
                str(item['MontoTotalLinea']),
                str(item['TipoItem']),
                str(item['UnidadMedida']),
                "",
                str(item['PorcDescuento']),
                str(item['ValorDescuento'])
            ]) + ";"
            lines.append(det)

        contenido_plano = "\n".join(lines)
        return contenido_plano

    def _extraer_folio(self, xml_respuesta):
        try:
            root = ET.fromstring(xml_respuesta)
            documento = root.find(".//Documento/Folio")
            if documento is not None:
                return documento.text
            else:
                return None
        except Exception:
            logger.exception("Error extrayendo folio del XML")
            return None

    # ---------------------- Operaciones externas ----------------------
    def _enviar_procesar_soap(self, contenido_plano_b64):
        """Llama al servicio Procesar y devuelve la respuesta (texto XML) o lanza excepción."""
        client = Client(self.wsdl_url)
        params = {
            'login': self._base64_login(),
            'file': contenido_plano_b64,
            'formato': "1"
        }
        return client.service.Procesar(**params)

    def _obtener_ticket(self, tipo_dte, folio):
        client = Client(self.wsdl_url)
        params = {
            'login': self._base64_login(),
            'ticket': base64.b64encode(f"ticket@{tipo_dte}@{folio}".encode()).decode()
        }
        return client.service.getBoletaTicket(**params)

    def _print_image_on_printer(self, pil_img: Image.Image):
        cfg = self.printer_cfg
        printer = None
        try:
            printer = Usb(cfg['vendor_id'], cfg['product_id'], in_ep=cfg.get('in_ep', 0x82), out_ep=cfg.get('out_ep', 0x02))
            # escpos Usb.image expects a PIL image; algunos drivers requieren 1-bit o RGB
            printer.image(pil_img)
            return True
        finally:
            try:
                if printer is not None:
                    printer.close()
            except Exception:
                pass

    def _print_text_on_printer(self, text: str, cut=False):
        cfg = self.printer_cfg
        printer = None
        try:
            printer = Usb(cfg['vendor_id'], cfg['product_id'], in_ep=cfg.get('in_ep', 0x82), out_ep=cfg.get('out_ep', 0x02))
            printer.text(text + "\n")
            if cut:
                printer.cut()
            return True
        finally:
            try:
                if printer is not None:
                    printer.close()
            except Exception:
                pass

    def _imprimir_ticket_xml(self, xml_data: str):
        """Intenta imprimir usando el XML devuelto por facturacion.cl. Devuelve True si se imprimió correctamente."""
        try:
            # Extraer campos base64 dentro de <Mensaje>
            def safe_b64decode(elem):
                if elem is None or elem.text is None:
                    return ""
                try:
                    return base64.b64decode(elem.text).decode('utf-8')
                except UnicodeDecodeError:
                    return base64.b64decode(elem.text).decode('latin-1')

            root = ET.fromstring(xml_data)
            mensaje = root.find('Mensaje')
            if mensaje is None:
                logger.error("No se encontró <Mensaje> en XML de ticket")
                return False

            head = safe_b64decode(mensaje.find('Head'))
            foot = safe_b64decode(mensaje.find('Foot'))
            ted = safe_b64decode(mensaje.find('TED'))
            
            logger.info(f"{head}")
            logger.info(f"{foot}")
            logger.info(f"{ted}")

            # Generar codigo PDF417 y convertir a imagen
            codes = encode(ted, columns=24, security_level=5)
            img = render_image(codes, scale=3)
            bw_img = img.convert('1')
            # Redimensionar si excede ancho del papel (max ~384 px para 58mm a 203 DPI)
            max_width = 570
            if bw_img.width > max_width:
                new_height = int((max_width / bw_img.width) * bw_img.height)
                bw_img = bw_img.resize((max_width, new_height), Image.LANCZOS)
            # Imprimir: texto (head), imagen y texto (foot)
            try:
                self._print_text_on_printer(head)
                self._print_image_on_printer(bw_img)
                self._print_text_on_printer(foot + "\ncreado por facturacion.cl - " + datetime.now().strftime('%d-%m-%Y %H:%M:%S'), cut=True)
                
                logger.info("Ticket impreso desde XML")
                return True
            except Exception as e:
                logger.exception(f"Error imprimiendo ticket desde XML: {e}")
                return False

        except Exception as e:
            logger.exception(f"Error procesando XML del ticket para imprimir: {e}")
            return False

    def _imprimir_fallback(self, payload: dict):
        """Imprime un comprobante local simple cuando no es posible generar boleta en el servicio remoto."""
        try:
            lines = []
            lines.append("*** BOLETA LOCAL (Sin conexión) ***")
            lines.append(f"Fecha: {datetime.now().isoformat(' ')}")
            lines.append(f"Monto pagado: {payload.get('monto_pagado')}")
            lines.append(f"Cantidad: {payload.get('cantidad_fichas')}")
            lines.append(f"Valor unitario: {payload.get('valor_unitario')}")
            lines.append("")
            lines.append("No fue posible generar la boleta fiscal en facturacion.cl. Esta es una constancia de venta.")
            lines.append("")
            lines.append("Gracias por su compra")
            text = '\n'.join(lines)

            try:
                ok = self._print_text_on_printer(text)
                if ok:
                    logger.info("Impresion fallback realizada")
                    return True
                else:
                    logger.error("La impresora devolvió error en fallback")
                    return False
            except Exception:
                logger.exception("Error imprimiendo fallback")
                return False
        except Exception:
            logger.exception("Error preparando fallback")
            return False

    # ---------------------- Lógica principal: slot conectado a la señal ----------------------
    @Slot(dict)
    def _on_generate_and_print(self, payload: dict):
        """Flujo completo: guardar en cola -> intentar enviar -> si falla imprimir fallback -> eliminar de cola.

        payload debe contener: monto_pagado, cantidad_fichas, valor_unitario
        """
        context = payload.copy()
        logger.info(f"Inicio proceso boleta: {context}")
        self.started.emit(context)

        # Guardar copia en cola para persistencia
        queue_path = None
        try:
            queue_path = self._save_to_queue(context)
        except Exception:
            logger.exception("No se pudo guardar boleta en cola en disco, se continúa en memoria")

        try:
            # 1) Crear contenido plano y codificar
            contenido = self._crear_contenido_plano(context['monto_pagado'], context['cantidad_fichas'], context['valor_unitario'])
            contenido_b64 = base64.b64encode(contenido.encode('utf-8')).decode()

            # 2) Llamar al servicio SOAP Procesar
            try:
                response = self._enviar_procesar_soap(contenido_b64)
                folio = self._extraer_folio(response)
                if folio:
                    logger.info(f"Folio generado: {folio}")
                    self.folio_generated.emit(str(folio))
                else:
                    logger.warning("No se obtuvo folio del servicio (respuesta inesperada)")

                # 3) Si tenemos folio, obtener ticket y tratar de imprimir
                
                if folio:
                    time.sleep(1)
                    try:
                        xml_ticket = self._obtener_ticket(39, folio)
                        if xml_ticket:
                            printed_ok = self._imprimir_ticket_xml(xml_ticket)
                            if printed_ok:
                                self.printed.emit({'folio': folio, **context})
                            else:
                                # Impresora dió error al imprimir ticket: continuar, eliminar de cola
                                logger.warning("Impresora falló al imprimir el ticket XML; se intentará continuar y eliminar boleta de la cola")
                                self.error.emit('printer_error', {'detail': 'Error imprimiendo ticket XML', **context})
                        else:
                            logger.warning("No se pudo obtener XML del ticket; se imprimirá comprobante fallback")
                            fallback_ok = self._imprimir_fallback(context)
                            if fallback_ok:
                                self.printed.emit({'fallback': True, **context})
                    except Exception as e:
                        logger.exception(f"Error durante obtencion/impression de ticket: {e}")
                        # Si falla en este punto, hacemos fallback
                        fallback_ok = self._imprimir_fallback(context)
                        if fallback_ok:
                            self.printed.emit({'fallback': True, **context})

                else:
                    # No se generó folio: imprimir fallback
                    logger.warning("No se generó folio, se imprimirá comprobante fallback")
                    fallback_ok = self._imprimir_fallback(context)
                    if fallback_ok:
                        self.printed.emit({'fallback': True, **context})

                # Al final, si la impresora tuvo problemas o no, SE ELIMINA la boleta de la cola para evitar reintentos duplicados
                if queue_path:
                    try:
                        self._remove_from_queue(queue_path)
                    except Exception:
                        logger.exception("No se pudo eliminar boleta de cola")

                self.finished.emit({'success': True, **context})
                return

            except Exception as e:
                # Errores de red/soap: imprimir fallback
                logger.exception(f"Error al procesar boleta por SOAP: {e}")
                self.error.emit('soap_error', {'detail': str(e), **context})
                fallback_ok = self._imprimir_fallback(context)
                if queue_path:
                    # Eliminamos la boleta de la cola aunque hubo error para evitar duplicados
                    self._remove_from_queue(queue_path)
                if fallback_ok:
                    self.printed.emit({'fallback': True, **context})
                self.finished.emit({'success': False, 'reason': 'soap_error', **context})
                return

        except Exception as e:
            logger.exception(f"Error inesperado en flujo de boleta: {e}")
            self.error.emit('unexpected', {'detail': traceback.format_exc(), **context})
            # En caso de fallo total intentamos eliminar de cola para evitar reintentos
            if queue_path:
                self._remove_from_queue(queue_path)
            self.finished.emit({'success': False, 'reason': 'unexpected', **context})
            return

