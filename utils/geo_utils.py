"""
MÓDULO GEO_UTILS - FINAX OS
Geolocalização e dados geográficos de Angola

Funcionalidade:
- Obtenção de coordenadas a partir de endereços (geocoding)
- Cálculo de distância entre pontos (fórmula de Haversine)
- Validação de províncias angolanas
- Tratamento de falhas de conexão
"""

import sys
import os
import math
from typing import Tuple, Optional, List

# Adiciona a pasta raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Raio da Terra em quilómetros
RAIO_TERRA_KM = 6371.0

# Lista oficial das 18 províncias de Angola
PROVINCIAS_ANGOLA: List[str] = [
    "Bengo",
    "Benguela",
    "Bié",
    "Cabinda",
    "Cuando Cubango",
    "Cuanza Norte",
    "Cuanza Sul",
    "Cunene",
    "Huambo",
    "Huíla",
    "Luanda",
    "Lunda Norte",
    "Lunda Sul",
    "Malanje",
    "Moxico",
    "Namibe",
    "Uíge",
    "Zaire"
]

# Províncias em ordem alfabética
PROVINCIAS_ANGOLA_SORTED: List[str] = sorted(PROVINCIAS_ANGOLA)

# Valores padrão para quando a geolocalização falha
COORDENADAS_PADRAO = {
    "lat": -8.8399,  # Centro aproximado de Angola (Luanda)
    "lon": 13.2894
}

# Mensagens
MSG_SEM_INTERNET = "⚠️ Sem conexão com a internet. Usando coordenadas padrão."
MSG_ENDERECO_NAO_ENCONTRADO = "Endereço não encontrado. Usando coordenadas padrão."
MSG_GEOCODING_DISPONIVEL = "✅ Serviço de geocodificação disponível."
MSG_GEOCODING_INDISPONIVEL = "❌ Serviço de geocodificação indisponível (falta de internet)."
MSG_DISTANCIA = "📍 Distância entre casa e escola: {:.2f} km"


# ============================================
# CLASSE PRINCIPAL DE GEOLOCALIZAÇÃO
# ============================================

class GeoUtils:
    """
    Classe responsável por geolocalização e dados geográficos de Angola.
    
    Funcionalidades:
    - Obter coordenadas a partir de endereços (geocoding)
    - Calcular distância entre pontos (Haversine)
    - Validar províncias angolanas
    - Tratamento de falhas de conexão
    """
    
    def __init__(self):
        """Inicializa o módulo de geolocalização"""
        
        self.geolocator = None
        self._inicializar_geolocator()
    
    def _inicializar_geolocator(self) -> None:
        """
        Inicializa o geocodificador Nominatim.
        Tenta importar e configurar, mas não falha se não estiver disponível.
        """
        try:
            from geopy.geocoders import Nominatim
            
            self.geolocator = Nominatim(user_agent="finax_os_angola")
            # Definir timeout como atributo após criação
            if hasattr(self.geolocator, 'timeout'):
                self.geolocator.timeout = 10
            
            # Testar conexão com uma consulta simples
            try:
                resultado = self.geolocator.geocode("Luanda, Angola", timeout=5)
                if resultado:
                    self.interface.mostrar_sucesso(MSG_GEOCODING_DISPONIVEL)
                else:
                    self.geolocator = None
                    self.interface.exibir_mensagem(MSG_GEOCODING_INDISPONIVEL, tipo="info")
            except Exception:
                self.geolocator = None
                self.interface.exibir_mensagem(MSG_GEOCODING_INDISPONIVEL, tipo="info")
                
        except ImportError:
            self.geolocator = None
            self.interface.exibir_mensagem(
                "⚠️ Biblioteca 'geopy' não instalada. Execute: pip install geopy",
                tipo="info"
            )
        except Exception as e:
            self.geolocator = None
            self.interface.exibir_mensagem(
                f"⚠️ Erro ao inicializar geolocalização: {e}",
                tipo="info"
            )
    
    # ============================================
    # 1. OBTER COORDENADAS
    # ============================================
    
    def obter_coordenadas(self, endereco: str) -> Tuple[float, float]:
        """
        Converte um endereço em coordenadas (latitude, longitude).
        
        Args:
            endereco (str): Endereço (ex: 'Maianga, Luanda, Angola')
        
        Returns:
            tuple: (latitude, longitude) ou coordenadas padrão se falhar
        """
        if not endereco or not endereco.strip():
            self.interface.exibir_mensagem("Endereço vazio.", tipo="info")
            return COORDENADAS_PADRAO["lat"], COORDENADAS_PADRAO["lon"]
        
        # Garantir que o endereço inclui Angola para melhor precisão
        if "Angola" not in endereco and "angola" not in endereco.lower():
            endereco_completo = f"{endereco}, Angola"
        else:
            endereco_completo = endereco
        
        # Se o geocodificador não está disponível, retorna padrão
        if self.geolocator is None:
            self.interface.exibir_mensagem(MSG_SEM_INTERNET, tipo="info")
            return COORDENADAS_PADRAO["lat"], COORDENADAS_PADRAO["lon"]
        
        try:
            # Tentar geocodificar
            location = self.geolocator.geocode(endereco_completo, timeout=10)
            
            if location:
                return location.latitude, location.longitude
            else:
                self.interface.exibir_mensagem(MSG_ENDERECO_NAO_ENCONTRADO, tipo="info")
                return COORDENADAS_PADRAO["lat"], COORDENADAS_PADRAO["lon"]
                
        except Exception as e:
            self.interface.exibir_mensagem(
                f"Erro ao obter coordenadas: {e}",
                tipo="info"
            )
            return COORDENADAS_PADRAO["lat"], COORDENADAS_PADRAO["lon"]
    
    # ============================================
    # 2. CÁLCULO DE DISTÂNCIA (HAVERSINE)
    # ============================================
    
    def calcular_distancia(self, 
                           lat1: float, lon1: float,
                           lat2: float, lon2: float) -> float:
        """
        Calcula a distância entre dois pontos usando a fórmula de Haversine.
        
        Args:
            lat1 (float): Latitude do ponto 1
            lon1 (float): Longitude do ponto 1
            lat2 (float): Latitude do ponto 2
            lon2 (float): Longitude do ponto 2
        
        Returns:
            float: Distância em quilómetros
        """
        # Converter para radianos
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Fórmula de Haversine
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distancia = RAIO_TERRA_KM * c
        
        return round(distancia, 2)
    
    def calcular_distancia_escola(self, 
                                   lat_aluno: float, lon_aluno: float,
                                   lat_escola: float, lon_escola: float) -> float:
        """
        Calcula a distância entre a casa do aluno e a escola.
        Wrapper da função calcular_distancia.
        
        Args:
            lat_aluno (float): Latitude da casa do aluno
            lon_aluno (float): Longitude da casa do aluno
            lat_escola (float): Latitude da escola
            lon_escola (float): Longitude da escola
        
        Returns:
            float: Distância em quilómetros
        """
        distancia = self.calcular_distancia(lat_aluno, lon_aluno, lat_escola, lon_escola)
        
        # Exibir mensagem informativa
        print(self.interface.cores.CIANO + MSG_DISTANCIA.format(distancia) + self.interface.cores.RESET)
        
        return distancia
    
    # ============================================
    # 3. VALIDAÇÃO DE PROVÍNCIAS DE ANGOLA
    # ============================================
    
    def validar_provincia_angola(self, provincia: str) -> bool:
        """
        Verifica se a província existe na lista oficial das 18 províncias de Angola.
        
        Args:
            provincia (str): Nome da província
        
        Returns:
            bool: True se válida, False caso contrário
        """
        if not provincia or not provincia.strip():
            return False
        
        provincia_normalizada = provincia.strip().title()
        
        # Verificar na lista
        for p in PROVINCIAS_ANGOLA:
            if provincia_normalizada == p:
                return True
        
        return False
    
    def listar_provincias(self) -> List[str]:
        """
        Retorna a lista das 18 províncias de Angola.
        
        Returns:
            list: Lista ordenada das províncias
        """
        return PROVINCIAS_ANGOLA_SORTED.copy()
    
    def obter_provincias_formatadas(self) -> str:
        """
        Retorna as províncias formatadas para exibição.
        
        Returns:
            str: Lista formatada das províncias
        """
        return ", ".join(PROVINCIAS_ANGOLA_SORTED)
    
    def exibir_provincias(self) -> None:
        """
        Exibe a lista das 18 províncias de Angola no terminal.
        """
        self.interface.mostrar_titulo("🏛️ PROVÍNCIAS DE ANGOLA")
        
        print(f"\n{self.interface.cores.CIANO}As 18 províncias de Angola são:{self.interface.cores.RESET}")
        
        # Exibir em colunas
        colunas = 3
        for i in range(0, len(PROVINCIAS_ANGOLA_SORTED), colunas):
            linha = []
            for j in range(colunas):
                if i + j < len(PROVINCIAS_ANGOLA_SORTED):
                    linha.append(f"   • {PROVINCIAS_ANGOLA_SORTED[i + j]}")
            print("".join(linha))
    
    # ============================================
    # 4. FUNÇÕES ADICIONAIS
    # ============================================
    
    def obter_coordenadas_escola_padrao(self) -> Tuple[float, float]:
        """
        Retorna coordenadas padrão para a escola (centro de Luanda).
        
        Returns:
            tuple: (latitude, longitude)
        """
        return COORDENADAS_PADRAO["lat"], COORDENADAS_PADRAO["lon"]
    
    def esta_disponivel(self) -> bool:
        """
        Verifica se o serviço de geolocalização está disponível.
        
        Returns:
            bool: True se disponível
        """
        return self.geolocator is not None
    
    def testar_conexao(self) -> bool:
        """
        Testa a conexão com o serviço de geocodificação.
        
        Returns:
            bool: True se funcionando
        """
        if self.geolocator is None:
            return False
        
        try:
            result = self.geolocator.geocode("Luanda, Angola", timeout=5)
            return result is not None
        except Exception:
            return False


# ============================================
# FUNÇÕES DE CONVENIÊNCIA (API SIMPLES)
# ============================================

def obter_coordenadas(endereco: str) -> Tuple[float, float]:
    """
    Função de conveniência para obter coordenadas.
    
    Args:
        endereco (str): Endereço
    
    Returns:
        tuple: (latitude, longitude)
    """
    geo = GeoUtils()
    return geo.obter_coordenadas(endereco)


def calcular_distancia(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Função de conveniência para calcular distância.
    
    Args:
        lat1, lon1: Coordenadas do ponto 1
        lat2, lon2: Coordenadas do ponto 2
    
    Returns:
        float: Distância em km
    """
    geo = GeoUtils()
    return geo.calcular_distancia(lat1, lon1, lat2, lon2)


def validar_provincia(provincia: str) -> bool:
    """
    Função de conveniência para validar província.
    
    Args:
        provincia (str): Nome da província
    
    Returns:
        bool: True se válida
    """
    geo = GeoUtils()
    return geo.validar_provincia_angola(provincia)


def listar_provincias() -> List[str]:
    """
    Função de conveniência para listar províncias.
    
    Returns:
        list: Lista das 18 províncias
    """
    geo = GeoUtils()
    return geo.listar_provincias()


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Geolocalização")
    print("=" * 60)
    
    geo = GeoUtils()
    
    # Testar listagem de províncias
    print("\n📋 PROVÍNCIAS DE ANGOLA:")
    print("-" * 40)
    for i, p in enumerate(geo.listar_provincias(), 1):
        print(f"   {i:2d}. {p}")
    
    # Testar validação de província
    print("\n🔍 TESTE DE VALIDAÇÃO DE PROVÍNCIAS:")
    print("-" * 40)
    testes = ["Luanda", "Luandaa", "Huambo", "Caxito", "Benguela"]
    for t in testes:
        valido = geo.validar_provincia_angola(t)
        resultado = "✅ Válida" if valido else "❌ Inválida"
        print(f"   {t}: {resultado}")
    
    # Testar geocodificação (se disponível)
    print("\n📍 TESTE DE GEOLOCALIZAÇÃO:")
    print("-" * 40)
    
    if geo.esta_disponivel():
        endereco = "Maianga, Luanda, Angola"
        lat, lon = geo.obter_coordenadas(endereco)
        print(f"   Endereço: {endereco}")
        print(f"   Coordenadas: {lat:.6f}, {lon:.6f}")
        
        # Testar cálculo de distância
        print("\n📏 TESTE DE CÁLCULO DE DISTÂNCIA:")
        print("-" * 40)
        
        # Coordenadas de exemplo (Luanda e Benguela)
        luanda_lat, luanda_lon = -8.8399, 13.2894
        benguela_lat, benguela_lon = -12.5783, 13.4072
        
        distancia = geo.calcular_distancia(luanda_lat, luanda_lon, benguela_lat, benguela_lon)
        print(f"   Distância Luanda ↔ Benguela: {distancia:.2f} km")
        
    else:
        print("   ⚠️ Serviço de geolocalização indisponível.")
        print("   Para usar, instale: pip install geopy")
    
    print("\n✅ Teste concluído!")