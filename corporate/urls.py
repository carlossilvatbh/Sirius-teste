from django.urls import path
from . import views
from .views_entity_library import entity_library_view
from .views_entity_library_enhanced import (
    entity_library_enhanced_view,
    create_entity_from_template_api,
    quick_add_entity_api,
    template_details_api,
    entity_usage_stats_enhanced_api,
    search_entities_api,
    search_parties_api
)
from .views_ownership_matrix import (
    ownership_matrix_visual_view,
    ownership_matrix_data_api,
    create_ownership_api,
    get_ownership_api,
    update_ownership_api,
    delete_ownership_api,
    validate_ownership_matrix_api,
    export_ownership_matrix_api
)
from .views_party_dashboard import (
    party_ownership_dashboard,
    party_dashboard_data,
    export_party_report,
    validate_party_ownership
)
from .views_organogram_printing import (
    organogram_printing_view,
    generate_organogram_report,
    download_report,
    preview_organogram
)
from .admin_navigation import sirius_main_dashboard
from .views_organogram_builder import (
    organogram_builder_view,
    organogram_builder_structure,
    organogram_builder_api,
    get_structure_data_api
)

app_name = 'corporate'

urlpatterns = [
    # Dashboard Principal SIRIUS
    path('dashboard/', sirius_main_dashboard, name='sirius_dashboard'),
    
    # Organogram Builder (Fase 1)
    path('build-organogram/', organogram_builder_view, name='organogram_builder'),
    path('build-organogram/<int:structure_id>/', organogram_builder_structure, name='organogram_builder_structure'),
    path('organogram-builder-api/', organogram_builder_api, name='organogram_builder_api'),
    path('api/structure-data/<int:structure_id>/', get_structure_data_api, name='get_structure_data_api'),
    
    # Original entity library
    path('entity-library/', entity_library_view, name='entity_library'),
    
    # Enhanced entity library (Fase 2)
    path('entity-library-enhanced/', entity_library_enhanced_view, name='entity_library_enhanced'),
    
    # Template APIs
    path('api/create-entity-from-template/', create_entity_from_template_api, name='create_entity_from_template_api'),
    path('api/quick-add-entity/', quick_add_entity_api, name='quick_add_entity_api'),
    path('api/template-details/<int:template_id>/', template_details_api, name='template_details_api'),
    
    # Enhanced stats APIs
    path('api/entity-usage-stats-enhanced/<int:entity_id>/', entity_usage_stats_enhanced_api, name='entity_usage_stats_enhanced_api'),
    
    # Search APIs
    path('api/search-entities/', search_entities_api, name='search_entities_api'),
    path('api/search-parties/', search_parties_api, name='search_parties_api'),
    
    # Ownership Matrix Visual (Fase 3)
    path('ownership-matrix-visual/', ownership_matrix_visual_view, name='ownership_matrix_visual'),
    
    # Ownership Matrix APIs
    path('api/ownership-matrix-data/', ownership_matrix_data_api, name='ownership_matrix_data_api'),
    path('api/ownership/', create_ownership_api, name='create_ownership_api'),
    path('api/ownership/<int:ownership_id>/', get_ownership_api, name='get_ownership_api'),
    path('api/ownership/<int:ownership_id>/update/', update_ownership_api, name='update_ownership_api'),
    path('api/ownership/<int:ownership_id>/delete/', delete_ownership_api, name='delete_ownership_api'),
    path('api/validate-ownership-matrix/', validate_ownership_matrix_api, name='validate_ownership_matrix_api'),
    path('api/export-ownership-matrix/', export_ownership_matrix_api, name='export_ownership_matrix_api'),
    
    # Party Ownership Dashboard (Fase 4)
    path('party-dashboard/', party_ownership_dashboard, name='party_ownership_dashboard'),
    path('party-dashboard/<int:party_id>/', party_ownership_dashboard, name='party_ownership_dashboard_detail'),
    path('api/party-dashboard-data/<int:party_id>/', party_dashboard_data, name='party_dashboard_data'),
    path('api/export-party-report/', export_party_report, name='export_party_report'),
    path('api/validate-party-ownership/<int:party_id>/', validate_party_ownership, name='validate_party_ownership'),
    
    # Organogram Printing (Fase 5)
    path('organogram-printing/', organogram_printing_view, name='organogram_printing'),
    path('api/generate-organogram-report/', generate_organogram_report, name='generate_organogram_report'),
    path('api/preview-organogram/', preview_organogram, name='preview_organogram'),
    path('download-report/<str:filename>/', download_report, name='download_report'),
]