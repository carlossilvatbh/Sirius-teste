# Generated by Django 4.2.7 on 2025-07-09 12:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('parties', '0001_initial'),
        ('corporate', '0001_initial'),
        ('corporate_relationship', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jurisdictionalert',
            name='service_connection',
            field=models.ForeignKey(blank=True, help_text='Associated service for this alert', null=True, on_delete=django.db.models.deletion.SET_NULL, to='corporate_relationship.service'),
        ),
        migrations.AddField(
            model_name='entityownership',
            name='owned_entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ownerships_as_owned', to='corporate.entity'),
        ),
        migrations.AddField(
            model_name='entityownership',
            name='owner_entity',
            field=models.ForeignKey(blank=True, help_text='Entity owner', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ownerships_as_owner', to='corporate.entity'),
        ),
        migrations.AddField(
            model_name='entityownership',
            name='owner_ubo',
            field=models.ForeignKey(blank=True, help_text='UBO owner', null=True, on_delete=django.db.models.deletion.CASCADE, to='parties.party'),
        ),
        migrations.AddField(
            model_name='entityownership',
            name='structure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entity_ownerships', to='corporate.structure'),
        ),
        migrations.AddIndex(
            model_name='entity',
            index=models.Index(fields=['jurisdiction'], name='corporate_e_jurisdi_51401c_idx'),
        ),
        migrations.AddIndex(
            model_name='entity',
            index=models.Index(fields=['active'], name='corporate_e_active_fe823f_idx'),
        ),
        migrations.AddIndex(
            model_name='entity',
            index=models.Index(fields=['entity_type'], name='corporate_e_entity__438d47_idx'),
        ),
        migrations.AddIndex(
            model_name='entity',
            index=models.Index(fields=['complexity'], name='corporate_e_complex_af5254_idx'),
        ),
        migrations.AddIndex(
            model_name='validationrule',
            index=models.Index(fields=['parent_entity'], name='corporate_v_parent__7dcdc7_idx'),
        ),
        migrations.AddIndex(
            model_name='validationrule',
            index=models.Index(fields=['related_entity'], name='corporate_v_related_d8c4fd_idx'),
        ),
        migrations.AddIndex(
            model_name='validationrule',
            index=models.Index(fields=['active'], name='corporate_v_active_e1675d_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='validationrule',
            unique_together={('parent_entity', 'related_entity', 'relationship_type')},
        ),
        migrations.AddIndex(
            model_name='successor',
            index=models.Index(fields=['ubo_proprietario', 'ativo'], name='corporate_s_ubo_pro_0d1a9f_idx'),
        ),
        migrations.AddIndex(
            model_name='successor',
            index=models.Index(fields=['data_efetivacao'], name='corporate_s_data_ef_673ee8_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='successor',
            unique_together={('ubo_proprietario', 'ubo_sucessor')},
        ),
        migrations.AlterUniqueTogether(
            name='structureownership',
            unique_together={('parent', 'child')},
        ),
        migrations.AddIndex(
            model_name='masterentity',
            index=models.Index(fields=['structure'], name='corporate_m_structu_4cd3e3_idx'),
        ),
        migrations.AddIndex(
            model_name='masterentity',
            index=models.Index(fields=['entity'], name='corporate_m_entity__dca7e0_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='masterentity',
            unique_together={('structure', 'entity')},
        ),
        migrations.AddIndex(
            model_name='jurisdictionalert',
            index=models.Index(fields=['jurisdicao', 'tipo_alerta'], name='corporate_j_jurisdi_06c724_idx'),
        ),
        migrations.AddIndex(
            model_name='jurisdictionalert',
            index=models.Index(fields=['next_deadline'], name='corporate_j_next_de_9674b2_idx'),
        ),
        migrations.AddIndex(
            model_name='jurisdictionalert',
            index=models.Index(fields=['deadline_type'], name='corporate_j_deadlin_06399b_idx'),
        ),
        migrations.AddIndex(
            model_name='jurisdictionalert',
            index=models.Index(fields=['prioridade'], name='corporate_j_priorid_0c94b8_idx'),
        ),
        migrations.AddIndex(
            model_name='jurisdictionalert',
            index=models.Index(fields=['ativo'], name='corporate_j_ativo_46580c_idx'),
        ),
        migrations.AddIndex(
            model_name='entityownership',
            index=models.Index(fields=['structure'], name='corporate_e_structu_9b3653_idx'),
        ),
        migrations.AddIndex(
            model_name='entityownership',
            index=models.Index(fields=['owned_entity'], name='corporate_e_owned_e_9cd9c1_idx'),
        ),
        migrations.AddIndex(
            model_name='entityownership',
            index=models.Index(fields=['owner_ubo'], name='corporate_e_owner_u_92f87e_idx'),
        ),
        migrations.AddIndex(
            model_name='entityownership',
            index=models.Index(fields=['owner_entity'], name='corporate_e_owner_e_a82a53_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='entityownership',
            unique_together={('structure', 'owner_ubo', 'owner_entity', 'owned_entity')},
        ),
    ]
