import xml.etree.ElementTree as ET
import defusedxml.ElementTree as SafeET
from typing import Dict, Any, List, Optional
from core.domain.entities.file import File
from core.domain.interfaces.xml_parser import IXmlParser
from core.domain.exceptions import InvalidXMLError, TagsNotFoundError

class XmlAdapter(IXmlParser):
    """
    Adaptador para parsing e extração de dados de arquivos XML.
    Funcionalidades principais:
    - Validação de sintaxe XML
    - Extração hierárquica de dados (preserva estrutura pai-filho)
    - Detecção automática de elementos repetidos
    - Geração de estatísticas (tags totais, preenchidas, vazias)
    - Suporte a tags prioritárias para relatórios
    - Agrupamento inteligente de tags similares
    """

    def validate(self, file: File) -> bool:
        """Valida se o conteúdo do arquivo é um XML bem formado."""
        try:
            # parseamento de xml seguro contra XXE
            SafeET.fromstring(file.content)
            return True
        except ET.ParseError:
            raise InvalidXMLError("O arquivo enviado não é um XML válido. Verifique a sintaxe.")

    def __clean_tag(self, tag: str) -> str:
        """Remove namespaces de tags XML."""
        if "}" in tag:
            return tag.split("}", 1)[1]
        return tag

    def extract(self, file: File, tags: Optional[List[str]] = None, priority_tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Extrai dados do XML de forma hierárquica."""
        try:
            # parseamento de xml seguro contra XXE
            root = SafeET.fromstring(file.content)
        except ET.ParseError:
            raise InvalidXMLError("O arquivo enviado não é um XML válido. Verifique a sintaxe.")

        # Inicializa contadores de estatísticas
        total_tags = 0
        filled_tags = 0
        empty_tags = 0

        # Estruturas de dados para retorno
        hierarchical_data = [] # Dados hierárquicos para Excel
        priority_data = [] # Dados prioritários para PDF
        grouped_data = {} # Dados agrupados para PDF
        alerts = [] # Alertas sobre qualidade dos dados

        # MODO UNIFICADO: Busca por elementos repetidos ou usa a raiz
        def find_repeated_elements(elem):
            """Busca recursivamente por elementos repetidos em qualquer nível da árvore XML."""
            children = list(elem)
            if not children:
                return None, []

            # Agrupa filhos por nome de tag
            tag_counts = {}
            for child in children:
                tag_cleaned = self.__clean_tag(child.tag)
                if tag_cleaned not in tag_counts:
                    tag_counts[tag_cleaned] = []
                tag_counts[tag_cleaned].append(child)

            # Verifica se há tags repetidas neste nível
            for tag_name, elements in tag_counts.items():
                if len(elements) > 1:
                    # Encontrou! Retorna imediatamente
                    return tag_name, elements

            # Não encontrou neste nível: busca recursivamente nos filhos
            for child in children:
                tag_name, elements = find_repeated_elements(child)
                if elements:
                    return tag_name, elements

            return None, []

        if tags:
            # Validação inicial de tags (específico)
            tags_lower = {t.lower() for t in tags}
            file_tags_cleaned = {self.__clean_tag(elem.tag).lower() for elem in root.iter()}

            missing_tags = []
            for tag in tags:
                tag_lower = tag.lower()
                # Valida se pelo menos o leaf (tag final) existe no arquivo
                leaf = tag_lower.split('_')[-1]
                if leaf not in file_tags_cleaned:
                    missing_tags.append(tag)

            if missing_tags:
                raise TagsNotFoundError(f"As seguintes tags não foram encontradas no arquivo: {', '.join(missing_tags)}")

        # Executa a busca por elementos repetidos
        repeated_tag, repeated_elements = find_repeated_elements(root)

        # MODO AUTOMÁTICO (DEFAULT): Foco em padrões repetidos, com fallback para registro único
        if not tags:
            if not repeated_elements:
                # Fallback: Se não há repetição, processa o root como registro único
                elements_to_process = [root]
                alerts.append("ℹ️ Nenhum padrão repetido encontrado. Processando como registro único.")
            else:
                elements_to_process = repeated_elements

            context_data = {} # Sem enriquecimento global no modo automático

        # MODO BUSCA AVANÇADA (TAGS ESPECIFICADAS)
        else:
            # Identifica caminho estrutural para autorizar seleção de containers
            structural_tags = set()
            if repeated_elements:
                structural_tags.add(repeated_tag.lower())
                def find_path_to_elem(current, target_elem, path):
                    if current == target_elem: return True
                    for child in current:
                        if find_path_to_elem(child, target_elem, path):
                            path.add(self.__clean_tag(current.tag).lower())
                            return True
                    return False
                find_path_to_elem(root, repeated_elements[0], structural_tags)

            # Enriquecimento Global: Captura tags do nível superior (singletons)
            context_data = {}
            if repeated_elements:
                context_data = self._extract_hierarchical(root, priority_tags, exclude_tag=repeated_tag)

            # Fallback para root se não houver repetidos (permite processar XMLs simples se tags forem pedidas)
            elements_to_process = repeated_elements if repeated_elements else [root]

        # PROCESSA CADA ELEMENTO (REGISTROS)
        all_unique_keys = set()
        filled_count = 0
        empty_count = 0

        for elem in elements_to_process:
            # Merge de contexto e dados específicos
            elem_data = context_data.copy()
            specific_data = self._extract_hierarchical(elem, priority_tags)
            elem_data.update(specific_data)

            if elem_data:
                item_to_add = None
                if tags:
                    structural_selected = any(st in tags_lower for st in structural_tags) if 'structural_tags' in locals() else False

                    # LÓGICA DE MATCHING ROBUSTA PARA CAMINHOS HIERÁRQUICOS
                    def matches_any_tag(k_low, requested_tags):
                        for t_low in requested_tags:
                            # 1. Match exato ou k é filho de t (user quer tudo dentro de t)
                            if k_low == t_low or k_low.startswith(t_low + "_"):
                                return True

                            # 2. Caso t inclua a raiz mas k não (rooting mismatch)
                            # Verificamos se algum sufixo do caminho t bate com o início de k
                            t_segs = t_low.split('_')
                            if len(t_segs) > 1:
                                for i in range(1, len(t_segs)):
                                    partial_t = "_".join(t_segs[i:])
                                    if k_low == partial_t or k_low.startswith(partial_t + "_"):
                                        return True

                            # 3. Caso t seja apenas uma parte do caminho de k (ex: busca por container no meio)
                            # Se t aparece como um bloco completo no caminho de k
                            if f"_{t_low}_" in f"_{k_low}_" or k_low.endswith("_" + t_low):
                                return True

                        return False

                    filtered = {
                        k: v for k, v in elem_data.items() 
                        if structural_selected or matches_any_tag(k.lower(), tags_lower)
                    }
                    if filtered: item_to_add = filtered
                else:
                    item_to_add = elem_data

                if item_to_add:
                    hierarchical_data.append(item_to_add)

                    # Coleta chaves únicas e conta preenchidas/vazias individualmente
                    for k, val in item_to_add.items():
                        all_unique_keys.add(k)
                        if val and str(val).strip():
                            filled_count += 1
                        else:
                            empty_count += 1

        # CÁLCULO DE ESTATÍSTICAS
        total_tags = len(all_unique_keys)
        filled_tags = filled_count
        empty_tags = empty_count

        # PROCESSA DADOS PRIORITÁRIOS
        # Extrai valores das tags marcadas como prioritárias para destaque no PDF
        if priority_tags and hierarchical_data:
            priority_tags_lower = {t.lower() for t in priority_tags}
            for item in hierarchical_data:
                for key, value in item.items():
                    if key.lower() in priority_tags_lower and value:
                        priority_data.append({'nome': key, 'valor': value})

        # AGRUPA DADOS SIMILARES
        # Agrupa tags por prefixo para organização no PDF
        grouped_data = self._group_similar_tags(hierarchical_data)

        # GERA ALERTAS
        # Avisos sobre qualidade/tamanho do XML
        if empty_tags > 0:
            alerts.append(f"⚠️ {empty_tags} tags vazias encontradas no processamento")

        if total_tags > 500:
            alerts.append(f"ℹ️ Grande volume de dados processados ({total_tags} tags)")

        return self._build_result(hierarchical_data, total_tags, filled_tags, empty_tags, priority_data, grouped_data, alerts)

    def _build_result(self, items, total, filled, empty, priority, groups, alerts) -> Dict[str, Any]:
        """Auxiliar para formatar o dicionário de retorno padrão."""
        return {
            "items": items,
            "hierarchical_data": items,
            "statistics": {
                "total": total,
                "preenchidas": filled,
                "vazias": empty
            },
            "tags_criticas": priority,
            "grupos": groups,
            "alerts": alerts
        }

    def _extract_hierarchical(self, elem: ET.Element, priority_tags: Optional[List[str]] = None, exclude_tag: Optional[str] = None, current_prefix: str = "") -> Dict[str, Any]:
        """Extrai dados de um elemento XML de forma hierárquica usando prefixos para aninhamento."""
        tag_cleaned = self.__clean_tag(elem.tag)

        # Ignora tags excluídas (útil para isolar dados de contexto)
        if exclude_tag and tag_cleaned == exclude_tag:
            return {}

        result = {}
        children = list(elem)

        if children:
            # Elemento tem filhos: processa cada filho recursivamente
            for child in children:
                child_tag = self.__clean_tag(child.tag)

                # Constrói o novo prefixo para manter a hierarquia no Excel
                new_prefix = f"{current_prefix}_{child_tag}" if current_prefix else child_tag

                if len(child) == 0:
                    # Filho é uma tag folha (com ou sem texto)
                    result[new_prefix] = child.text.strip() if child.text else ""
                else:
                    # Filho tem sub-filhos: recursão para extrair dados aninhados
                    sub_data = self._extract_hierarchical(child, priority_tags, exclude_tag, current_prefix=new_prefix)
                    result.update(sub_data)
        else:
            # Elemento não tem filhos: extrai texto direto (caso base)
            tag_name = f"{current_prefix}_{tag_cleaned}" if current_prefix else tag_cleaned
            result[tag_name] = elem.text.strip() if elem.text else ""

        return result

    def _count_tags(self, elem: ET.Element) -> Dict[str, int]:
        """Conta estatísticas de tags em um elemento XML."""
        total = 0
        filled = 0
        empty = 0

        for child in elem.iter():
            total += 1

            # Verifica se é tag pai (tem filhos)
            has_children = len(list(child)) > 0

            if has_children:
                # Tag pai: não conta como vazia (é apenas estrutural)
                pass
            elif child.text and child.text.strip():
                # Tag filha com texto: conta como preenchida
                filled += 1
            else:
                # Tag filha sem texto: conta como vazia
                empty += 1

        return {"total": total, "filled": filled, "empty": empty}

    def _group_similar_tags(self, data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa tags similares por prefixo para organização no PDF."""
        groups = {}

        # Coleta todas as chaves únicas de todos os items
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())

        # Agrupa por prefixo
        for key in all_keys:
            if '_' in key:
                # Tag com underscore: usa parte antes do _ como prefixo
                prefix = key.split('_')[0]
            else:
                # Tag sem underscore: usa a tag completa
                prefix = key

            prefix = prefix.capitalize()

            if prefix not in groups:
                groups[prefix] = []

            # Adiciona valores dessa chave de todos os items
            for item in data:
                if key in item:
                    groups[prefix].append({'nome': key, 'valor': item[key]})

        return groups