import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv

# 添加项目根目录到 PATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / '.env')

from utils.notify import NotificationKit


@pytest.fixture
def notification_kit(monkeypatch):
	monkeypatch.setenv('EMAIL_USER', 'test@example.com')
	monkeypatch.setenv('EMAIL_PASS', 'test-password')
	monkeypatch.setenv('EMAIL_TO', 'receiver@example.com')
	monkeypatch.setenv('PUSHPLUS_TOKEN', 'test_token')
	monkeypatch.setenv('DINGDING_WEBHOOK', 'https://example.com/dingtalk')
	monkeypatch.setenv('FEISHU_WEBHOOK', 'https://example.com/feishu')
	monkeypatch.setenv('WEIXIN_WEBHOOK', 'https://example.com/wecom')
	return NotificationKit()


def test_real_notification(notification_kit):
	"""真实接口测试，需要配置.env.local文件"""
	if os.getenv('ENABLE_REAL_TEST') != 'true':
		pytest.skip('未启用真实接口测试')

	notification_kit.push_message(
		'测试消息', f'这是一条测试消息\n发送时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
	)


@patch('smtplib.SMTP_SSL')
def test_send_email(mock_smtp, notification_kit):
	mock_server = MagicMock()
	mock_smtp.return_value.__enter__.return_value = mock_server

	notification_kit.send_email('测试标题', '测试内容')

	assert mock_server.login.called
	assert mock_server.send_message.called


@patch('utils.notify.curl_requests.post')
def test_send_pushplus(mock_post, notification_kit):
	notification_kit.send_pushplus('测试标题', '测试内容')

	mock_post.assert_called_once()
	args = mock_post.call_args[1]
	assert 'test_token' in str(args)


@patch('utils.notify.curl_requests.post')
def test_send_dingtalk(mock_post, notification_kit):
	notification_kit.send_dingtalk('测试标题', '测试内容')

	expected_webhook = 'https://example.com/dingtalk'
	expected_data = {'msgtype': 'text', 'text': {'content': '测试标题\n测试内容'}}

	mock_post.assert_called_once_with(expected_webhook, json=expected_data, timeout=30)


@patch('utils.notify.curl_requests.post')
def test_send_feishu(mock_post, notification_kit):
	notification_kit.send_feishu('测试标题', '测试内容')

	mock_post.assert_called_once()
	args = mock_post.call_args[1]
	assert 'card' in args['json']


@patch('utils.notify.curl_requests.post')
def test_send_wecom(mock_post, notification_kit):
	notification_kit.send_wecom('测试标题', '测试内容')

	mock_post.assert_called_once_with(
		'https://example.com/wecom', json={'msgtype': 'text', 'text': {'content': '测试标题\n测试内容'}}, timeout=30
	)


def test_missing_config(monkeypatch):
	for key in ('EMAIL_USER', 'EMAIL_PASS', 'EMAIL_TO', 'PUSHPLUS_TOKEN'):
		monkeypatch.delenv(key, raising=False)
	kit = NotificationKit()

	with pytest.raises(ValueError, match='Email configuration not set'):
		kit.send_email('测试', '测试')

	with pytest.raises(ValueError, match='PushPlus Token not configured'):
		kit.send_pushplus('测试', '测试')


@patch('utils.notify.NotificationKit.send_email')
@patch('utils.notify.NotificationKit.send_dingtalk')
@patch('utils.notify.NotificationKit.send_wecom')
@patch('utils.notify.NotificationKit.send_pushplus')
@patch('utils.notify.NotificationKit.send_feishu')
def test_push_message(mock_feishu, mock_pushplus, mock_wecom, mock_dingtalk, mock_email, notification_kit):
	notification_kit.push_message('测试标题', '测试内容')

	assert mock_email.called
	assert mock_dingtalk.called
	assert mock_wecom.called
	assert mock_pushplus.called
	assert mock_feishu.called
