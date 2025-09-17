#!/usr/bin/env python3
"""
Tests for cli.py - Command Line Interface
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from src.cli import main


class TestCLI:
    """Test CLI functionality"""
    
    def test_main_no_args(self, capsys):
        """Test main with no arguments"""
        with patch('sys.argv', ['cli.py']):
            main()
            captured = capsys.readouterr()
            assert "IPLM - IP Management System" in captured.out
    
    def test_main_help(self, capsys):
        """Test main with help argument"""
        with patch('sys.argv', ['cli.py', '--help']):
            with pytest.raises(SystemExit):
                main()
            captured = capsys.readouterr()
            assert "IPLM - IP Management System" in captured.out
    
    def test_db_init_command(self, capsys):
        """Test db init command"""
        with patch('sys.argv', ['cli.py', 'db', 'init']):
            with patch('src.cli.db_manager') as mock_db:
                mock_db.connect.return_value = True
                mock_db.create_tables.return_value = None
                
                main()
                captured = capsys.readouterr()
                assert "Database initialized successfully!" in captured.out
                mock_db.connect.assert_called_once()
                mock_db.create_tables.assert_called_once()
    
    def test_db_init_connection_failed(self, capsys):
        """Test db init when connection fails"""
        with patch('sys.argv', ['cli.py', 'db', 'init']):
            with patch('src.cli.db_manager') as mock_db:
                mock_db.connect.return_value = False
                
                with pytest.raises(SystemExit) as excinfo:
                    main()
                assert excinfo.value.code == 1
                
                captured = capsys.readouterr()
                assert "Failed to connect to database" in captured.err
    
    def test_db_status_command(self, capsys):
        """Test db status command"""
        with patch('sys.argv', ['cli.py', 'db', 'status']):
            with patch('src.cli.db_manager') as mock_db:
                mock_db.connect.return_value = True
                mock_db.connection.is_connected.return_value = True
                
                main()
                captured = capsys.readouterr()
                assert "Database connection successful!" in captured.out
    
    def test_db_status_connection_failed(self, capsys):
        """Test db status when connection fails"""
        with patch('sys.argv', ['cli.py', 'db', 'status']):
            with patch('src.cli.db_manager') as mock_db:
                mock_db.connect.return_value = False
                
                with pytest.raises(SystemExit) as excinfo:
                    main()
                assert excinfo.value.code == 1
                
                captured = capsys.readouterr()
                assert "Database connection failed" in captured.err
    
    def test_process_list_command(self, capsys):
        """Test process list command"""
        with patch('sys.argv', ['cli.py', 'process', 'list']):
            with patch('src.cli.Process') as mock_process:
                mock_process1 = Mock()
                mock_process1.id = 1
                mock_process1.name = "Process1"
                mock_process1.node = "28nm"
                mock_process1.fab = "TSMC"
                
                mock_process2 = Mock()
                mock_process2.id = 2
                mock_process2.name = "Process2"
                mock_process2.node = "7nm"
                mock_process2.fab = "Samsung"
                
                mock_process.find_all.return_value = [mock_process1, mock_process2]
                
                main()
                captured = capsys.readouterr()
                assert "1: Process1 (Node: 28nm, FAB: TSMC)" in captured.out
                assert "2: Process2 (Node: 7nm, FAB: Samsung)" in captured.out
    
    def test_process_create_command(self, capsys):
        """Test process create command"""
        with patch('sys.argv', ['cli.py', 'process', 'create']):
            with patch('src.cli.Process') as mock_process:
                with patch('builtins.input', side_effect=['Test_Process', '28nm', 'TSMC', 'Test description']):
                    mock_instance = Mock()
                    mock_instance.save.return_value = True
                    mock_process.return_value = mock_instance
                    
                    main()
                    captured = capsys.readouterr()
                    assert "Process 'Test_Process' created successfully!" in captured.out
                    mock_instance.save.assert_called_once()
    
    def test_process_create_failure(self, capsys):
        """Test process create when save fails"""
        with patch('sys.argv', ['cli.py', 'process', 'create']):
            with patch('src.cli.Process') as mock_process:
                with patch('builtins.input', side_effect=['Test_Process', '28nm', 'TSMC', 'Test description']):
                    mock_instance = Mock()
                    mock_instance.save.return_value = False
                    mock_process.return_value = mock_instance
                    
                    main()
                    captured = capsys.readouterr()
                    assert "Failed to create process" in captured.err
    
    def test_process_show_command(self, capsys):
        """Test process show command"""
        with patch('sys.argv', ['cli.py', 'process', 'show']):
            with patch('src.cli.Process') as mock_process:
                with patch('builtins.input', return_value='Test_Process'):
                    mock_instance = Mock()
                    mock_instance.to_dict.return_value = {
                        'id': 1,
                        'name': 'Test_Process',
                        'node': '28nm',
                        'fab': 'TSMC',
                        'description': 'Test description'
                    }
                    mock_process.find_by_name.return_value = mock_instance
                    
                    main()
                    captured = capsys.readouterr()
                    assert '"name": "Test_Process"' in captured.out
    
    def test_process_show_not_found(self, capsys):
        """Test process show when not found"""
        with patch('sys.argv', ['cli.py', 'process', 'show']):
            with patch('src.cli.Process') as mock_process:
                with patch('builtins.input', return_value='NonExistent'):
                    mock_process.find_by_name.return_value = None
                    
                    main()
                    captured = capsys.readouterr()
                    assert "Process not found" in captured.err
    
    def test_type_list_command(self, capsys):
        """Test type list command"""
        with patch('sys.argv', ['cli.py', 'type', 'list']):
            with patch('src.cli.Type') as mock_type:
                mock_type1 = Mock()
                mock_type1.id = 1
                mock_type1.name = "Type1"
                mock_type1.path = "Type1"
                mock_type1.level = 0
                
                mock_type2 = Mock()
                mock_type2.id = 2
                mock_type2.name = "Type2"
                mock_type2.path = "Type1/Type2"
                mock_type2.level = 1
                
                mock_type.find_all.return_value = [mock_type1, mock_type2]
                
                main()
                captured = capsys.readouterr()
                assert "Type1 (ID: 1, Path: Type1)" in captured.out
                assert "Type2 (ID: 2, Path: Type1/Type2)" in captured.out
    
    def test_type_create_command(self, capsys):
        """Test type create command"""
        with patch('sys.argv', ['cli.py', 'type', 'create']):
            with patch('src.cli.Type') as mock_type:
                with patch('builtins.input', side_effect=['Test_Type', '', 'Test description']):
                    mock_instance = Mock()
                    mock_instance.save.return_value = True
                    mock_type.return_value = mock_instance
                    
                    main()
                    captured = capsys.readouterr()
                    assert "Type 'Test_Type' created successfully!" in captured.out
                    mock_instance.save.assert_called_once()
    
    def test_type_create_with_parent(self, capsys):
        """Test type create with parent"""
        with patch('sys.argv', ['cli.py', 'type', 'create']):
            with patch('src.cli.Type') as mock_type:
                with patch('builtins.input', side_effect=['Child_Type', '1', 'Test description']):
                    mock_instance = Mock()
                    mock_instance.save.return_value = True
                    mock_type.return_value = mock_instance
                    
                    main()
                    captured = capsys.readouterr()
                    assert "Type 'Child_Type' created successfully!" in captured.out
    
    def test_type_tree_command(self, capsys):
        """Test type tree command"""
        with patch('sys.argv', ['cli.py', 'type', 'tree']):
            with patch('src.cli.print_type_tree') as mock_print_tree:
                main()
                mock_print_tree.assert_called_once()
    
    def test_ip_list_command(self, capsys):
        """Test ip list command"""
        with patch('sys.argv', ['cli.py', 'ip', 'list']):
            with patch('src.cli.IP') as mock_ip:
                with patch('src.cli.Process') as mock_process:
                    with patch('src.cli.Type') as mock_type:
                        mock_ip1 = Mock()
                        mock_ip1.id = 1
                        mock_ip1.name = "IP1"
                        mock_ip1.status = "alpha"
                        mock_ip1.process_id = 1
                        mock_ip1.type_id = 1
                        
                        mock_process1 = Mock()
                        mock_process1.name = "Process1"
                        
                        mock_type1 = Mock()
                        mock_type1.path = "Type1"
                        
                        mock_ip.find_all.return_value = [mock_ip1]
                        mock_process.find_by_id.return_value = mock_process1
                        mock_type.find_by_id.return_value = mock_type1
                        
                        main()
                        captured = capsys.readouterr()
                        assert "1: IP1 (Status: alpha, IP Type Path: Type1, Process: Process1)" in captured.out
    
    def test_ip_create_command(self, capsys):
        """Test ip create command"""
        with patch('sys.argv', ['cli.py', 'ip', 'create']):
            with patch('src.cli.IP') as mock_ip:
                with patch('src.cli.Type') as mock_type:
                    with patch('src.cli.Process') as mock_process:
                        with patch('builtins.input', side_effect=['Test_IP', 'Type1', 'Process1', '1.0', 'alpha', 'Provider', 'Description']):
                            mock_type_instance = Mock()
                            mock_type_instance.id = 1
                            mock_type.find_by_name.return_value = mock_type_instance
                            
                            mock_process_instance = Mock()
                            mock_process_instance.id = 1
                            mock_process.find_by_name.return_value = mock_process_instance
                            
                            mock_ip_instance = Mock()
                            mock_ip_instance.save.return_value = True
                            mock_ip.return_value = mock_ip_instance
                            
                            main()
                            captured = capsys.readouterr()
                            assert "IP 'Test_IP' created successfully!" in captured.out
    
    def test_ip_create_type_not_found(self, capsys):
        """Test ip create when type not found"""
        with patch('sys.argv', ['cli.py', 'ip', 'create']):
            with patch('src.cli.Type') as mock_type:
                with patch('builtins.input', side_effect=['Test_IP', 'NonExistentType', 'Process1','','','','']):
                    mock_type.find_by_name.return_value = None
                    
                    with pytest.raises(SystemExit) as excinfo:
                        main()
                    assert excinfo.value.code == 1

                    captured = capsys.readouterr()
                    assert "Type not found" in captured.err
    
    def test_ip_create_process_not_found(self, capsys):
        """Test ip create when process not found"""
        with patch('sys.argv', ['cli.py', 'ip', 'create']):
            with patch('src.cli.Type') as mock_type:
                with patch('src.cli.Process') as mock_process:
                    with patch('builtins.input', side_effect=['Test_IP', 'Type1', 'NonExistentProcess','','','','']):
                        mock_type_instance = Mock()
                        mock_type_instance.id = 1
                        mock_type.find_by_name.return_value = mock_type_instance
                        
                        mock_process.find_by_name.return_value = None

                        with pytest.raises(SystemExit) as excinfo:
                            main()
                        assert excinfo.value.code == 1
                
                        captured = capsys.readouterr()
                        assert "Process not found" in captured.err

    def test_ip_show_command(self, capsys):
        """Test ip show command"""
        with patch('sys.argv', ['cli.py', 'ip', 'show']):
            with patch('src.cli.IP') as mock_ip:
                with patch('builtins.input', return_value='Test_IP'):
                    mock_instance = Mock()
                    mock_instance.to_dict.return_value = {
                        'id': 1,
                        'name': 'Test_IP',
                        'type_id': 1,
                        'process_id': 1,
                        'status': 'alpha'
                    }
                    mock_instance.get_type.return_value = Mock()
                    mock_instance.get_type.return_value.to_dict.return_value = {'name': 'Type1'}
                    mock_instance.get_process.return_value = Mock()
                    mock_instance.get_process.return_value.to_dict.return_value = {'name': 'Process1'}
                    mock_ip.find_by_name.return_value = mock_instance
                    
                    main()
                    captured = capsys.readouterr()
                    assert '"name": "Test_IP"' in captured.out
    
    def test_ip_find_command(self, capsys):
        """Test ip find command"""
        with patch('sys.argv', ['cli.py', 'ip', 'find']):
            with patch('src.cli.ip_manager') as mock_ip_manager:
                with patch('builtins.input', side_effect=['Test_IP', '', 'alpha', 'Provider']):
                    mock_ip = Mock()
                    mock_ip.id = 1
                    mock_ip.name = "Test_IP"
                    mock_ip.status = "alpha"
                    mock_ip.type_id = 1
                    
                    mock_ip_manager.find.return_value = [mock_ip]
                    
                    main()
                    captured = capsys.readouterr()
                    assert "1: Test_IP (Status: alpha, Type: 1)" in captured.out
    
    def test_ip_release_command(self, capsys):
        """Test ip release command"""
        with patch('sys.argv', ['cli.py', 'ip', 'release']):
            with patch('src.cli.ip_manager') as mock_ip_manager:
                with patch('builtins.input', return_value='Test_IP'):
                    mock_ip_manager.release.return_value = True
                    
                    main()
                    captured = capsys.readouterr()
                    assert "IP 'Test_IP' released successfully!" in captured.out
    
    def test_ip_release_failure(self, capsys):
        """Test ip release when it fails"""
        with patch('sys.argv', ['cli.py', 'ip', 'release']):
            with patch('src.cli.ip_manager') as mock_ip_manager:
                with patch('builtins.input', return_value='Test_IP'):
                    mock_ip_manager.release.return_value = False
                    
                    main()
                    captured = capsys.readouterr()
                    assert "Failed to release IP" in captured.err
    
    def test_ip_update_command(self, capsys):
        """Test ip update command"""
        with patch('sys.argv', ['cli.py', 'ip', 'update']):
            with patch('src.cli.ip_manager') as mock_ip_manager:
                with patch('builtins.input', side_effect=['Test_IP', 'New_Name', 'production', 'New description']):
                    mock_ip_manager.update.return_value = True
                    
                    main()
                    captured = capsys.readouterr()
                    assert "IP 'Test_IP' updated successfully!" in captured.out
    
    def test_ip_tree_command_all(self, capsys):
        """Test ip tree command showing all trees"""
        with patch('sys.argv', ['cli.py', 'ip', 'tree']):
            with patch('src.cli.ip_manager') as mock_ip_manager:
                main()
                mock_ip_manager.show_ip_tree.assert_called_once_with(show_details=False)
    
    def test_ip_tree_command_specific_ip(self, capsys):
        """Test ip tree command for specific IP"""
        with patch('sys.argv', ['cli.py', 'ip', 'tree', '--ip', 'Test_IP']):
            with patch('src.cli.ip_manager') as mock_ip_manager:
                main()
                mock_ip_manager.show_ip_tree.assert_called_once_with(ip_name='Test_IP', show_details=False)
    
    def test_ip_tree_command_with_details(self, capsys):
        """Test ip tree command with details"""
        with patch('sys.argv', ['cli.py', 'ip', 'tree', '--details']):
            with patch('src.cli.ip_manager') as mock_ip_manager:
                main()
                mock_ip_manager.show_ip_tree.assert_called_once_with(show_details=True)
    
    def test_ip_tree_command_by_process(self, capsys):
        """Test ip tree command by process"""
        with patch('sys.argv', ['cli.py', 'ip', 'tree', '--process', 'Test_Process']):
            with patch('src.cli.ip_manager') as mock_ip_manager:
                main()
                mock_ip_manager.show_ip_tree_by_process.assert_called_once_with(process_name='Test_Process', show_details=False)
    
    def test_ip_tree_command_by_type(self, capsys):
        """Test ip tree command by type"""
        with patch('sys.argv', ['cli.py', 'ip', 'tree', '--type', 'Test_Type']):
            with patch('src.cli.ip_manager') as mock_ip_manager:
                main()
                mock_ip_manager.show_ip_tree_by_type.assert_called_once_with(type_name='Test_Type', show_details=False)

