"""
Testes de integração para UseFile (caso de uso).
Testa lógica complexa:
- Fluxo completo de orquestração (4 etapas)
- Propagação de erros
- Notificações de progresso
"""

import pytest
import os
from core.application.use_cases.use_file import UseFile
from core.domain.entities.file import File
from core.domain.entities.processing_options import ProcessingOptions
from infrastructure.adapters.xml_adapter import XmlAdapter
from infrastructure.adapters.report_adapter import ReportAdapter
from infrastructure.adapters.storage_adapter import StorageAdapter
from core.domain.exceptions import InvalidXMLError, TagsNotFoundError, InvalidFormatError

@pytest.mark.integration
class TestUseFileCompleteFlow:
    """
    Testes para fluxo completo de processamento.
    LÓGICA COMPLEXA: Orquestração de 4 etapas
    1. Validação XML (0%)
    2. Extração de dados (30%)
    3. Geração de relatórios (60%)
    4. Salvamento de arquivos (90%)
    5. Conclusão (100%)
    """

    @pytest.mark.asyncio
    async def test_process_file_success(self, simple_xml, temp_output_dir, mock_notifier):
        """
        Deve processar arquivo com sucesso através de todas as etapas.
        Verifica:
        - Resultado de sucesso
        - Arquivos gerados (xlsx e pdf)
        - Notificações enviadas
        - Progresso final (100%)
        """
        # Setup: Cria adapters e caso de uso
        xml_adapter = XmlAdapter()
        report_adapter = ReportAdapter()
        storage_adapter = StorageAdapter()

        use_file = UseFile(xml_adapter, report_adapter, storage_adapter, mock_notifier)

        # Cria entidade File
        content = simple_xml.encode('utf-8')
        file = File(
            name="test.xml",
            content=content,
            size=len(content),
            extension="xml"
        )

        # Cria opções de processamento
        options = ProcessingOptions(
            formats=["xlsx", "pdf"],
            output_path=temp_output_dir
        )

        # Executa processamento
        result = await use_file.process_file(file, options)

        # Verifica resultado
        assert result['success'] is True
        assert 'Arquivos gerados com sucesso' in result['message']
        assert len(result['generated_files']) == 2

        # Verifica que arquivos foram criados
        for file_path in result['generated_files']:
            assert os.path.exists(file_path)

        # Verifica que notificações foram enviadas
        assert len(mock_notifier.notifications) > 0

        # Verifica notificação final
        last_notification = mock_notifier.get_last_notification()
        assert last_notification['progress'] == 1.0
        assert 'concluído' in last_notification['message'].lower()

    @pytest.mark.asyncio
    async def test_process_file_with_specific_tags(self, simple_xml, temp_output_dir, mock_notifier):
        """Deve processar arquivo com tags específicas."""
        xml_adapter = XmlAdapter()
        report_adapter = ReportAdapter()
        storage_adapter = StorageAdapter()

        use_file = UseFile(xml_adapter, report_adapter, storage_adapter, mock_notifier)

        content = simple_xml.encode('utf-8')
        file = File(name="test.xml", content=content, size=len(content), extension="xml")

        options = ProcessingOptions(
            tags=["NAME", "AGE"],
            formats=["xlsx"],
            output_path=temp_output_dir
        )

        result = await use_file.process_file(file, options)

        assert result['success'] is True
        assert len(result['generated_files']) == 1

@pytest.mark.integration
class TestUseFileErrorHandling:
    """
    Testes para tratamento e propagação de erros.
    Verifica que erros de domínio são propagados corretamente
    e notificações de erro são enviadas.
    """

    @pytest.mark.asyncio
    async def test_invalid_xml_error(self, invalid_xml, temp_output_dir, mock_notifier):
        """
        Deve lançar InvalidXMLError para XML malformado.
        Verifica:
        - Erro é lançado
        - Notificação de erro é enviada
        """
        xml_adapter = XmlAdapter()
        report_adapter = ReportAdapter()
        storage_adapter = StorageAdapter()

        use_file = UseFile(xml_adapter, report_adapter, storage_adapter, mock_notifier)

        content = invalid_xml.encode('utf-8')
        file = File(name="test.xml", content=content, size=len(content), extension="xml")

        options = ProcessingOptions(formats=["xlsx"], output_path=temp_output_dir)

        with pytest.raises(InvalidXMLError):
            await use_file.process_file(file, options)

        # Deve ter enviado notificação de erro
        last_notification = mock_notifier.get_last_notification()
        assert 'Erro' in last_notification['message']

    @pytest.mark.asyncio
    async def test_tags_not_found_error(self, simple_xml, temp_output_dir, mock_notifier):
        """Deve lançar TagsNotFoundError quando tags não existem."""
        xml_adapter = XmlAdapter()
        report_adapter = ReportAdapter()
        storage_adapter = StorageAdapter()

        use_file = UseFile(xml_adapter, report_adapter, storage_adapter, mock_notifier)

        content = simple_xml.encode('utf-8')
        file = File(name="test.xml", content=content, size=len(content), extension="xml")

        options = ProcessingOptions(
            tags=["NONEXISTENT"],
            formats=["xlsx"],
            output_path=temp_output_dir
        )

        with pytest.raises(TagsNotFoundError):
            await use_file.process_file(file, options)

    @pytest.mark.asyncio
    async def test_invalid_format_error(self, simple_xml, temp_output_dir, mock_notifier):
        """Deve lançar erro para formato inválido."""
        xml_adapter = XmlAdapter()
        report_adapter = ReportAdapter()
        storage_adapter = StorageAdapter()

        use_file = UseFile(xml_adapter, report_adapter, storage_adapter, mock_notifier)

        content = simple_xml.encode('utf-8')
        file = File(name="test.xml", content=content, size=len(content), extension="xml")

        # Deve falhar durante validação de opções
        with pytest.raises(ValueError):
            options = ProcessingOptions(
                formats=["invalid"],
                output_path=temp_output_dir
            )

    @pytest.mark.asyncio
    async def test_invalid_file_extension(self, simple_xml, temp_output_dir, mock_notifier):
        """Deve lançar erro para arquivo não-XML."""
        xml_adapter = XmlAdapter()
        report_adapter = ReportAdapter()
        storage_adapter = StorageAdapter()

        use_file = UseFile(xml_adapter, report_adapter, storage_adapter, mock_notifier)

        content = simple_xml.encode('utf-8')
        file = File(name="test.txt", content=content, size=len(content), extension="txt")

        options = ProcessingOptions(formats=["xlsx"], output_path=temp_output_dir)

        with pytest.raises(InvalidFormatError) as exc_info:
            await use_file.process_file(file, options)

        assert "extensão" in str(exc_info.value).lower()

@pytest.mark.integration
class TestUseFileProgressNotifications:
    """
    Testes para notificações de progresso.
    Verifica que notificações são enviadas em cada etapa do processamento.
    """

    @pytest.mark.asyncio
    async def test_progress_notifications_sent(self, simple_xml, temp_output_dir, mock_notifier):
        """
        Deve enviar notificações de progresso em cada etapa.
        Etapas esperadas:
        - 0.0: Validando XML
        - 0.3: Validando dados
        - 0.6: Gerando relatórios
        - 0.9: Salvando relatórios
        - 1.0: Processamento concluído
        """
        xml_adapter = XmlAdapter()
        report_adapter = ReportAdapter()
        storage_adapter = StorageAdapter()

        use_file = UseFile(xml_adapter, report_adapter, storage_adapter, mock_notifier)

        content = simple_xml.encode('utf-8')
        file = File(name="test.xml", content=content, size=len(content), extension="xml")

        options = ProcessingOptions(formats=["xlsx"], output_path=temp_output_dir)

        await use_file.process_file(file, options)

        # Deve ter múltiplas notificações
        assert len(mock_notifier.notifications) >= 4

        # Verifica progressão (0.0 -> 0.3 -> 0.6 -> 0.9 -> 1.0)
        progresses = [n['progress'] for n in mock_notifier.notifications]
        assert 0.0 in progresses
        assert 1.0 in progresses

        # Progresso deve ser crescente
        for i in range(len(progresses) - 1):
            assert progresses[i] <= progresses[i + 1]