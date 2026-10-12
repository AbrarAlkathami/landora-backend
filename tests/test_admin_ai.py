import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import pytest
from landora_backend.ai.admin import snapshot, answer_admin_question, AdminAnswer


def records():
    root = Path(__file__).resolve().parents[1] / 'data'
    parcels = [SimpleNamespace(**row) for row in json.loads((root/'sarj-lands-riyadh.json').read_text())]
    inquiries = [SimpleNamespace(**row) for row in json.loads((root/'investor-inquiries.json').read_text())]
    return parcels,inquiries


def test_snapshot_uses_complete_current_records():
    parcels,inquiries=records()
    result=snapshot(parcels,inquiries)
    assert result['summary']['total_parcels']==120
    assert result['summary']['available_parcels']==62
    assert result['summary']['total_inquiries']==48
    assert len(result['summary']['unmatched_inquiry_ids'])==14
    assert sum(result['summary']['open_demand_by_area'].values())==result['summary']['open_inquiries']
    assert result['summary']['budget_averages']['lease']['basis']=='annual rent'
    assert all('phone' not in q for q in result['inquiries'])


def test_closed_inquiries_are_removed_from_demand_and_unmatched():
    parcels,inquiries=records()
    for inquiry in inquiries: inquiry.status='closed'
    result=snapshot(parcels,inquiries)['summary']
    assert result['open_inquiries']==0
    assert result['unmatched_inquiry_ids']==[]
    assert result['open_demand_by_area']=={}


def test_admin_answer_is_generated_and_invalid_record_links_are_discarded():
    parcels,inquiries=records()
    session=Mock();session.scalars.side_effect=[Mock(all=lambda:parcels),Mock(all=lambda:inquiries)]
    context=Mock();context.__enter__=Mock(return_value=session);context.__exit__=Mock(return_value=False)
    generated=AdminAnswer(answer='تحليل مولّد من الذكاء الاصطناعي',parcel_ids=[parcels[0].parcel_id,'missing',parcels[0].parcel_id],inquiry_ids=[inquiries[0].inquiry_id,'missing'])
    client=Mock();client.responses.parse.return_value=SimpleNamespace(output_parsed=generated)
    with patch('landora_backend.ai.admin.SessionLocal',return_value=context):
        result=answer_admin_question('أين يتركز الطلب؟',client)
    assert result['answer']==generated.answer
    assert len(result['parcels'])==1 and len(result['inquiries'])==1
    request=client.responses.parse.call_args.kwargs
    assert request['model']=='gpt-5-mini'
    assert len(json.loads(request['input'])['business_data']['parcels'])==120
    assert 'Do not append follow-up questions' in request['instructions']


def test_invalid_model_output_does_not_fall_back_to_a_script():
    context=Mock();context.__enter__=Mock(return_value=Mock(scalars=lambda _:Mock(all=lambda:[])));context.__exit__=Mock(return_value=False)
    client=Mock();client.responses.parse.return_value=SimpleNamespace(output_parsed=None)
    with patch('landora_backend.ai.admin.SessionLocal',return_value=context), pytest.raises(RuntimeError):
        answer_admin_question('Overview',client)


def test_all_matching_inquiries_are_returned_as_cards():
    parcels, inquiries = records()
    matching = inquiries[:11]
    session = Mock()
    session.scalars.side_effect = [Mock(all=lambda: parcels), Mock(all=lambda: inquiries)]
    context = Mock()
    context.__enter__ = Mock(return_value=session)
    context.__exit__ = Mock(return_value=False)
    generated = AdminAnswer(
        answer='عدد الاستفسارات: 11. التفاصيل في البطاقات.',
        inquiry_ids=[inquiry.inquiry_id for inquiry in matching],
    )
    client = Mock()
    client.responses.parse.return_value = SimpleNamespace(output_parsed=generated)
    with patch('landora_backend.ai.admin.SessionLocal', return_value=context):
        result = answer_admin_question('اعطيني كل الناس الي استفسرو', client)
    assert [card['inquiry_id'] for card in result['inquiries']] == generated.inquiry_ids
    assert result['answer'] == generated.answer
