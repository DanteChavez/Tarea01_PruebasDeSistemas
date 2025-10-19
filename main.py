# Integrantes
# Dante Chavez
# Nikolas Lagos
# Max Latuz
import sys

import grpc
import distance_unary_pb2_grpc as pb2_grpc
import distance_unary_pb2 as pb2
from google.protobuf.json_format import MessageToJson
import json
import unittest
import math
from geo_location import *


class Prueba_distance_grpc_service(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_address = "localhost:50051"
        print(f"\nConectando al servidor en {cls.server_address}...")

    def setUp(self):
        self.channel = grpc.insecure_channel(self.server_address)
        self.stub = pb2_grpc.DistanceServiceStub(self.channel)

    def tearDown(self):
        self.channel.close()

    def test_PosicionMalFormada_SinInicial(self):
        message = pb2.SourceDest(
            source=pb2.Position(),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertEqual(-1, dic["distance"], f'Se esperaba distancia -1, obtenida {dic["distance"]}')

    def test_PosicionMalFormada_SinFinal(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=10, longitude=10),
            destination=pb2.Position(),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertEqual(-1, dic["distance"], f'Se esperaba distancia -1, obtenida {dic["distance"]}')

    def test_PosicionMalFormada_SinInicial_SinFinal(self):
        message = pb2.SourceDest(
            source=pb2.Position(),
            destination=pb2.Position(),
            unit="km"
        )
        try:
            response = self.stub.geodesic_distance(message)
            dic = json.loads(MessageToJson(response))
            self.assertEqual(-1, dic["distance"], f'Se esperaba distancia -1, obtenida {dic["distance"]}')
        except Exception as e:
            self.fail("No debe dar error y debe estar definida la distancia")

    def test_PosicionMalFormada_SinSource(self):
        message = pb2.SourceDest(
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertEqual(-1, dic["distance"], f'Se esperaba distancia -1, obtenida {dic["distance"]}')

    def test_PosicionMalFormada_SinDestination(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertEqual(-1, dic["distance"], f'Se esperaba distancia -1, obtenida {dic["distance"]}')

    def test_PosicionMalFormada_SinSource_SinDestination(self):
        message = pb2.SourceDest(
            unit="km"
        )
        try:
            response = self.stub.geodesic_distance(message)
            dic = json.loads(MessageToJson(response))
            self.assertEqual(-1, dic["distance"], f'Se esperaba distancia -1, obtenida {dic["distance"]}')
        except Exception as e:
            self.fail("No debe dar error y debe estar definida la distancia")

    def test_PosicionMalFormada_SinUnit(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=20, longitude=20),
            destination=pb2.Position(latitude=10, longitude=10),
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertEqual("km", dic["unit"], f'Se esperaba unidad en km, obtenida {dic["unit"]}')

    def test_PosicionMalFormada_unit_erronea(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=10, longitude=10),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="x"
        )
        try:
            response = self.stub.geodesic_distance(message)
            if response.distance == -1:
                self.assertTrue(1, 1)
        except:
            self.fail("No debe saltar error, debe devolver -1 en distancia e invalid en unidad de medida")

    def test_PosicionMalFormada_UnitMayusculas(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=20, longitude=20),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="KM"
        )
        try:
            response = self.stub.geodesic_distance(message)
            dic = json.loads(MessageToJson(response))
        except Exception as e:
            self.fail(f'El servicio lanzó un error inesperado: {str(e)}')

    def test_PosicionMalFormada_ValoresDiccionarioCasero(self):
        message = pb2.SourceDest(
            source={"latitude": 10, "longitude": 10},
            destination={"latitude": 20, "longitude": 20},
            unit="km",
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertNotEqual("km", dic["unit"], f'Se esperaba unidad fuera invalida, obtenida {dic["unit"]}')

    def test_PosicionMalFormada_ValoresDiccionarioCasero_fallo(self):
        message = {
            "source": {"latitude": 10, "longitude": 10},
            "destination": {"latitude": 20, "longitude": 20},
            "unit": "km"
        }
        try:
            response = self.stub.geodesic_distance(message)
            dic = json.loads(MessageToJson(response))
            self.fail(f'Se esperaba un error pero la operación tuvo éxito con unidad: {dic["unit"]}')
        except Exception as e:
            pass

    def test_posicionInicial_igual_posicionFinal(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=10, longitude=10),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        if (not 'distance' in dic):
            self.fail(f'Se esperaba distancia invalida (-1) o distancia 0 pero no se obtuvo {dic}')

        self.assertIn([-1, 0], dic['distance'], f'Se esperaba distancia invalida (-1) o distancia 0')

    def test_posicionInicial_igual_posicionFinal_enCeroCero(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=0),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        if (not 'distance' in dic):
            self.fail(f'Se esperaba distancia invalida (-1) o distancia 0 pero no se obtuvo {dic}')

        self.assertIn([-1, 0], dic['distance'], f'Se esperaba distancia invalida (-1) o distancia 0')

    def test_int_excede_32bits_con_signo(self):
        valor = 2147483647 + 1
        message = pb2.SourceDest(
            source=pb2.Position(latitude=valor, longitude=10),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        with self.assertRaises(Exception, msg=f"NO están bien definidos los límites para {valor}"):
            response = self.stub.geodesic_distance(message)

    def test_int_excede_64bits_con_signo(self):
        valor = 9223372036854775807 + 1
        message = pb2.SourceDest(
            source=pb2.Position(latitude=valor, longitude=10),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        with self.assertRaises(Exception, msg=f"NO están bien definidos los límites para {valor}"):
            response = self.stub.geodesic_distance(message)

    def test_int_excede_64bits_sin_signo(self):
        valor = 18446744073709551615 + 1
        message = pb2.SourceDest(
            source=pb2.Position(latitude=valor, longitude=10),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        with self.assertRaises(Exception, msg=f"NO están bien definidos los límites para {valor}"):
            response = self.stub.geodesic_distance(message)

    def test_int_numero_muy_grande(self):
        valor = 9999999999999999999999999999999
        message = pb2.SourceDest(
            source=pb2.Position(latitude=valor, longitude=10),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        with self.assertRaises(Exception, msg=f"NO están bien definidos los límites para {valor}"):
            response = self.stub.geodesic_distance(message)

    def test_PosicionMalDefinida_limite_superior_latitud(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=200, longitude=10),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertTrue(dic['distance'] == -1)

    def test_PosicionMalDefinida_limite_superior_longitud(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=10, longitude=200),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertTrue(dic['distance'] == -1)

    def test_PosicionMalDefinida_limite_superior_latitud_longitud(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=200, longitude=200),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertTrue(dic['distance'] == -1)

    def test_PosicionMalDefinida_limite_inferior_latitud(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=-200, longitude=10),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertTrue(dic['distance'] == -1)

    def test_PosicionMalDefinida_limite_inferior_longitud(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=10, longitude=-200),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertTrue(dic['distance'] == -1.0)

    def test_PosicionMalDefinida_limite_inferior_latitud_longitud(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=-200, longitude=-200),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertTrue(dic['distance'] == -1.0)

    def test_distancia_igualMeridiano_latitud(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=10, longitude=0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertAlmostEqual(respuesta.distance, 1111.0, delta=10.0)

    def test_distancia_igualParalelo_longitud(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=10),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertAlmostEqual(respuesta.distance, 1111, delta=10.0)

    def test_distancia_maximaDistancia(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=180),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertAlmostEqual(respuesta.distance, 20015.0, delta=50.0)

    def test_distancia_valida_latitud90Positivo(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=90.0, longitude=0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertEqual(respuesta.unit, "km")

    def test_distancia_valida_latitud90Negativo(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=-90.0, longitude=0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertEqual(respuesta.unit, "km")

    def test_distancia_valida_longitud180Positivo(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=180),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_distancia_valida_longitud180Negativo(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=-180),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_distancia_valida_valorFrontera_latitudSuperior(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=89.999, longitude=0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertEqual(respuesta.unit, "km")

    def test_distancia_valida_valorFrontera_latitudInferior(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=-89.999, longitude=0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_distancia_valida_valorFrontera_longitudSuperior(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=179.999),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_distancia_valida_valorFrontera_longitudInferior(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=-179.999),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")


class PruebaClasePosicion(unittest.TestCase):
    def test_limite_mayor_latitud(self):
        with self.assertRaises(ValueError, msg=f"Limite mayor latitud No definido"):
            hola = Position(10, 200, 0)

    def test_limite_mayor_longitud(self):
        with self.assertRaises(ValueError, msg=f"Limite mayor longitud No definido"):
            hola = Position(10, 200, 0)

    def test_limite_menor_latitud(self):
        with self.assertRaises(ValueError, msg=f"Limite menor latitud No definido"):
            hola = Position(-200, 10, 0)

    def test_limite_menor_longitud(self):
        with self.assertRaises(ValueError, msg=f"Limite menor longitud No definido"):
            hola = Position(10, -200, 0)


class Prueba_valoresFrontera(unittest.TestCase):
    def setUp(self):
        self.canal = grpc.insecure_channel("localhost:50051")
        self.stub = pb2_grpc.DistanceServiceStub(self.canal)

    def tearDown(self):
        self.canal.close()

    def test_distancia_geodesica_km(self):
        print(f"\n--- Ejecutando: {self.id()} ---")
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=-33.45, longitude=-70.66),
            destination=pb2.Position(latitude=-33.04, longitude=-71.62),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)

        distancia_esperada_km = 100.35
        try:
            self.assertEqual(respuesta.unit, "km")
            self.assertAlmostEqual(respuesta.distance, distancia_esperada_km, delta=1.0,
                                   msg="La distancia en KM no es la esperada.")
            print(
                f"Resultado: ÉXITO - La distancia ({respuesta.distance:.2f} km) coincide con la esperada ({distancia_esperada_km} km).")
        except AssertionError:
            print(
                f"Resultado: FALLO - Distancia calculada ({respuesta.distance:.2f} km) difiere de la esperada ({distancia_esperada_km} km).")
            raise

    def test_unidad_predeterminada_es_km(self):
        print(f"\n--- Ejecutando: {self.id()} ---")
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=-33.45, longitude=-70.66),
            destination=pb2.Position(latitude=-33.04, longitude=-71.62),
            unit=""
        )
        respuesta = self.stub.geodesic_distance(mensaje)

        distancia_esperada_km = 100.35
        try:
            self.assertEqual(respuesta.unit, "km", "La unidad predeterminada debe ser 'km'")
            self.assertAlmostEqual(respuesta.distance, distancia_esperada_km, delta=1.0)
            print(f"Resultado: ÉXITO - La unidad por defecto funcionó como se esperaba.")
        except AssertionError:
            print(
                f"Resultado: FALLO - Se calculó en millas náuticas ({respuesta.distance:.2f}) pero se reportó como 'km'.")
            raise

    def test_distancia_geodesica_nm(self):
        print(f"\n--- Ejecutando: {self.id()} ---")
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=-33.45, longitude=-70.66),
            destination=pb2.Position(latitude=-33.04, longitude=-71.62),
            unit="nm"
        )
        respuesta = self.stub.geodesic_distance(mensaje)

        distancia_esperada_nm = 54.18
        self.assertEqual(respuesta.unit, "nm")
        self.assertAlmostEqual(respuesta.distance, distancia_esperada_nm, delta=1.0,
                               msg="La distancia en NM no es la esperada.")
        print(
            f"Resultado: ÉXITO - El cálculo en millas náuticas ({respuesta.distance:.2f} nm) coincide con el esperado.")

    def test_distancia_cero_mismo_punto(self):
        print(f"\n--- Ejecutando: {self.id()} ---")
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=40.7128, longitude=-74.0060),
            destination=pb2.Position(latitude=40.7128, longitude=-74.0060),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)

        self.assertEqual(respuesta.distance, 0.0, "La distancia entre el mismo punto debe ser 0.")
        print("Resultado: ÉXITO - La distancia cero se calculó correctamente.")

    def test_valorFrontera_limiteDecimal3(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=90.000003, longitude=10),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )

        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertEqual(-1, dic['distance'], f'Deja pasar el valor 90.000003')

    def test_valorFrontera_limiteDecimal4(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=90.000004, longitude=10),
            destination=pb2.Position(latitude=10, longitude=10),
            unit="km"
        )

        response = self.stub.geodesic_distance(message)
        dic = json.loads(MessageToJson(response))
        self.assertEqual(-1, dic['distance'], f'Deja pasar el valor 90.000004')


class PruebaSistemaValoresFrontera(unittest.TestCase):
    def setUp(self):
        self.canal = grpc.insecure_channel("localhost:50051")
        self.stub = pb2_grpc.DistanceServiceStub(self.canal)

    def tearDown(self):
        self.canal.close()

    def test_servicio_latitud_90_punto_0(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=90.0, longitude=0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_servicio_latitud_menos_90_punto_0(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=-90.0, longitude=0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_servicio_latitud_90_entero(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=90, longitude=0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_servicio_latitud_menos_90_entero(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=-90, longitude=0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_servicio_latitud_89_punto_999(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=89.999, longitude=0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_servicio_latitud_menos_89_punto_999(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=-89.999, longitude=0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_servicio_longitud_180_entero(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=180),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_servicio_longitud_menos_180_entero(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=-180),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_servicio_longitud_180_punto_0(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=180.0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_servicio_longitud_menos_180_punto_0(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=-180.0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_servicio_longitud_179_punto_999(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=179.999),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

    def test_servicio_longitud_menos_179_punto_999(self):
        mensaje = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=-179.999),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(mensaje)
        self.assertTrue(isinstance(respuesta.distance, (int, float)))
        self.assertEqual(respuesta.unit, "km")

class DistanceServiceTestsRunner:
    tests = [
        Prueba_distance_grpc_service,
        PruebaClasePosicion,
        Prueba_valoresFrontera,
        PruebaSistemaValoresFrontera
    ]

    @staticmethod
    def runner_start():
        suite = unittest.TestSuite() # Contenedor de pruebas
        loader = unittest.TestLoader() # Busca los test, dentro de las clases
        # Busca los test en cada clase y los agrega al contenedor
        for test_class in DistanceServiceTestsRunner.tests:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        runner = unittest.TextTestRunner() # Ejecutor de pruebas
        result = runner.run(suite)  # Ejecutar las pruebas



if __name__ == "__main__":
    DistanceServiceTestsRunner.runner_start()
