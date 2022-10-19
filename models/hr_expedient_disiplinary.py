# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import time


class ExpedientStage(models.Model):
    _name = "hr.expedient.stage"
    _description = "Expedient Stage"
    _order = 'sequence,id'

    name = fields.Char("Stage Name", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=10, help='Gives the sequence order when displaying a list of stages.')
    #detalle
    expedient_ids = fields.Many2many('type.expedint', string="Expedient Specific",
                                     help='Specific jobs that uses this stage. Other jobs will not use this stage.')
    requirements = fields.Text("Requirements")
    fold = fields.Boolean(
        "Folded in Kanban",
        help="This stage is folded in the kanban view when there are no records in that stage to display.")
    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda self: _('Blocked'), translate=True, required=True)
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda self: _('Ready for Next Stage'), translate=True, required=True)
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda self: _('In Progress'), translate=True, required=True)

    @api.model
    def default_get(self, fields):
        if self._context and self._context.get('default_expedient_id') and not self._context.get(
                'hr_expedient_stage_mono', False):
            context = dict(self._context)
            context.pop('default_expedient_id')
            self = self.with_context(context)
        return super(ExpedientStage, self).default_get(fields)


class TypeExpedient(models.Model):
    _name = 'type.expedint'
    _description = 'Modelo para el registro los  tipos de expedientes:'

    def _compute_expedient_count(self):
        for rec in self:
            cantitad_expedientes = self.env["hr.expedient"].search_count(
                [("type_expedient_id", "=", rec.id), ("active", "=", True)]
            )
            rec.expedient_count = cantitad_expedientes

    # proceso  para la secuencia de  folio 01-09-2022
    name = fields.Char('Expedient Type', required=True)
    # res=fields.Many2one('hr.employee',string="Responsable")
    description = fields.Char('Description')
    active = fields.Boolean('Active', default=True, store=True, readonly=False)
    image = fields.Binary(string='Image')
    state = fields.Selection([
        ('progress', 'Expedient in Progress'),
        ('open', 'Expedient Open')
    ], string='Status', readonly=True, required=True, tracking=True, copy=False, default='progress',
        help="Set whether the investigation process is open or closed for this expedient.")
    color = fields.Integer()
    expedient_count = fields.Integer(compute='_compute_expedient_count', string="Expedient Count")

    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}


class Expedient(models.Model):
    _name = "hr.expedient"
    _description = "Expedient"
    _order = "id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    def _default_stage_id(self):
        if self._context.get('default_expedient_id'):
            return self.env['hr.expedient.stage'].search([
                ('fold', '=', False)
            ], order='sequence asc', limit=1).id
        return False

    # el proceso de prueba
    # def _get_default_stage_id(self):
    #     """ Gives default stage_id """
    #     type_expedient_id = self.env.context.get('default_type_expedient_id')
    #     if not type_expedient_id:
    #         return False
    #    return self.stage_find(type_expedient_id, [('fold', '=', False)])

    # proceso  para la secuencia de  folio 01-09-2022

    @api.model
    def create(self, vals):
        if vals.get('sequence_type') == 'RM/2022/':
            vals['name'] = self.env['ir.sequence'].next_by_code('typ.exped') or '/'
            # vals['name'] = self.pool.get('ir.sequence').next_by_code('typ.exped') or '/'
        if vals.get('sequence_type') == 'SC/2022/':
            vals['name'] = self.env['ir.sequence'].next_by_code('prueba.2') or '/'
            # vals['name'] = self.pool.get('ir.sequence').next_by_code('prueba.2') or '/'
        if vals.get('sequence_type') == 'AMP/2022/':
            vals['name'] = self.env['ir.sequence'].next_by_code('amp.exped') or '/'
            # vals['name'] = self.pool.get('ir.sequence').next_by_code('prueba.2') or '/'
        return super(Expedient, self).create(vals)

    # proceso  para la secuencia de  folio 01-09-2022

    # proceso  para la secuencia de  folio 01-09-2022
    sequence_type = fields.Selection(string='seque',
                                     selection=[('RM/2022/', 'REMOCION'), ('SC/2022/', 'SEPARACON DE CARGO'),
                                                ('AMP/2022/', 'AMPARO')])
    name = fields.Char("N° EXPEDIENTE") or 'New'
    # name = fields.Char("Subject / Expedient Name", required=True) or 'New'
    # name = fields.Char(string="Task No", readonly=True, required=True, copy=False, default='New')
    active = fields.Boolean("Active", default=True,
                            help="If the active field is set to false, it will allow you to hide the case without removing it.")
    # PRUEBA2+ viernes26-08-22
    # partner_id = fields.Many2one('res.partner',string='Asignar_Responsable')
    # prueba2*
    description = fields.Text("Description")
    #prueba  esta
    stage_id = fields.Many2one('hr.expedient.stage', 'ETAPA DE ESTATUS', ondelete='restrict', Tracking=True,
                               domain="['|', ('expedient_ids', '=', False), ('expedient_ids', '=', type_expedient_id)]",
                               copy=False, index=True, group_expand='_read_group_stage_ids', default=_default_stage_id)
    last_stage_id = fields.Many2one('hr.expedient.stage', 'Last Stage',
                                    help='Stage of the expedient before being in the current stage. Used for lost cases analysis.')
    date_open = fields.Date(string="FECHA DE APERTURA",   index=True)
    date_last_stage_update = fields.Datetime("Last Stage Update", index=True, default=fields.Datetime.now)
    type_expedient_id = fields.Many2one('type.expedint',string="TIPO DE EXPEDIENTE")
    # prueba para poner el nombre de expedienete
    name1 = fields.Char("new", related="type_expedient_id.name")
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked', readonly=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid', readonly=False)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing', readonly=False)
    source_id = fields.Char(string='PROCEDENCIA DE EXPEDIENTE')
    genero= fields.Char(string='GENERO')
    inv= fields.Char(string='UNIDAD INVOLUCRADA')
    #Selection([('Agencia de Administración Penitenciaria', 'Agencia de Administración Penitenciaria'), ('Asuntos Internos', 'Asuntos Internos'),('Asusntos Juridicos CEDH','Asusntos Juridicos CEDH'),('C.E.D.H','C.E.D.H'),('C-5','C-5'),('CERESO  Cadereyta','CERESO  Cadereyta'),('CERESO  Topo Chico','CERESO  Topo Chico'),('CERESO Apodaca','CERESO Apodaca'),('Comisario General de Proteccion Institucional','Comisario General de Proteccion Institucional'),('Contralora General de la Contraloría y Transparencia Gubernamental','Contralora General de la Contraloría y Transparencia Gubernamental'),('Fuerza Civil','Fuerza Civil'),('Queja por Escrito','Queja por Escrito'),('Queja Presencial','Queja Presencial'),('Secretaria de Seguridad Publica','Secretaria de Seguridad Publica'),('Unidad Anticorrupcion','Unidad Anticorrupcion')],string='PROCEDENCIA DE EXPEDIENTE',)
    file_origin = fields.Char(string='NO. DE DOCUMENTO ORIGEN')
    signing_person = fields.Char(string='QUIEN FIRMA')
    #Selection(([('Lic. Jorge Fernando Garza Morales Comisario General','Lic. Jorge Fernando Garza Morales Comisario General'),('Lic. Juan Antonio Guerrero Vargas  Director de Asuntos Jurídicos de la Secretaría de Seguridad Pública del estado','Lic. Juan Antonio Guerrero Vargas Director de Asuntos Jurídicos de la Secretaría de Seguridad Pública del estado'),('Lic. Vicente Hiram Blade Morales Encargado de la Inspección General y Asuntos Internos','Lic. Vicente Hiram Blade Morales   Encargado de la Inspección General y Asuntos Internos')]),string='QUIEN FIRMA')
    sender_dependency = fields.Char(string='INSTITUCIÓN O ÁREA DE ADSCRIPCIÓN')
    #se agrega
    date = fields.Date(string="FECHA DE OFICIO DE ORIGEN")
    date1= fields.Date(string='FECHA EN QUE INGRESA A LA C.H Y .J')
    adqui= fields.Char(string="PROCEDENCIA DENUNCIA")
    #Selection([('1er Grupo','1er Grupo'),('2do Grupo','2do Grupo'),('3er Grupo','3er Grupo'),('4rto Grupo','4rto Grupo'),('5to Grupo','5to Grupo'),('Aduana Vehicular','Aduana Vehicular'),('Alcaide de Centro Preventivo de Reinsercion Social','Alcaide de Centro Preventivo de Reinsercion Social'),('Bandera de Guerra','Bandera de Guerra'),('C.I.A.A.I','C.I.A.A.I'),('C-5','C-5'),('Centro de Internamiento y de Adaptacion para Adolescentes Infractores','Centro de Internamiento y de Adaptacion para Adolescentes Infractores'),('Centro Preventivo  y de Reinsercion Social de Topo Chico','Centro Preventivo  y de Reinsercion Social de Topo Chico'),('Cereso Apodaca','Cereso Apodaca'),('Cereso Cadereyta','Cereso Cadereyta'),('Cereso Topo Chico','Cereso Topo Chico'),('Comisario General','Comisario General')],string="ADSCRIPCIÓN")
    adqui1 = fields.Char(string="ADSCRIPCIÓN")
    conducta= fields.Char(string='CONDUCTA')
    #.Selection([('Faltas','Faltas'),('Conductas Prohibidas','Conductas Prohibidas'),('Faltas  Graves a los Principios de actuacion  y a las Normas de Disiplina','Faltas  Graves a los Principios de actuacion  y a las Normas de Disiplina'),('N/A','N/A')],string='CONDUCTA')
    accion= fields.Char(string="ACCION")
    #.Selection([('Abuso de Autoridad','Abuso de Autoridad'),('Abuso de Autoridad Lesiones Calificadas e Intimidacion','Abuso de Autoridad Lesiones Calificadas e Intimidacion'),('Abuso de Autoridad Robo','Abuso de Autoridad Robo'),('Abuso de Autoridad Robo Cohecho','Abuso de Autoridad Robo Cohecho'),('Acoso Laboral y sexual','Acoso Laboral y sexual'),('Actos de Corrupción','Actos de Corrupcion'),('Actos de Indisiplina en el Servicio o Fuera de el','Actos de Indisiplina en el Servicio o Fuera de el'),('Actos de Indisiplina en el Servicio o Fuera de el Portacion de drogas E Ingerir Bebidas Alcoholicas dentro de la Inst','Actos de Indisiplina en el Servicio o Fuera de el Portacion de drogas E Ingerir Bebidas Alcoholicas dentro de la Inst')],string='ACCION')
    Hechos= fields.Char(string='DESCRIPCIÓN DE LOS HECHOS')
    Sancion=fields.Char(string="SANCION")
    #.Selection([('Causada Ejecutoria','Causada Ejecutoria'),('Cierre por Comite','Cierre por Comite'),('Desechamiento','Desechamiento'),('Desistimento','Desistimento'),('N/A','N/A'),('No incurrio por Responsabilidad','No incurrio por Responsabilidad'),('No Inicio','No Inicio'),('Prescripcion','Prescripcion'),('Se acúmulo con 07/2016','Se acúmulo con 07/2016')],string='SANCION')
    #Cierre=fields.Char("")
    #.Selection([('Amonestacion Privada','Amonestacion Privada'),('Amparo','Amparo'),('Asunto totalmente Concluida','Asunto totalmente Concluida'),('Asunto totalmente Concluida No existe Suficientes Elementos de Prueba','Asunto totalmente Concluida No existe Suficientes Elementos de Prueba'),('Suspencion de Funciones','Suspencion de Funciones')],string='MOTIVO DE CIERRE')
    motdcierre=fields.Char(string="MOTIVO DE CIERRE")
    Finalizacion=fields.Char(string="FINALIZACION")
    #.Selection([('Amonestacion Privada','Amonestacion Privada'),('Amparo','Amparo'),('Asunto Totalmente Concluido','Asunto Totalmente Concluido'),('Asunto Totalmente Concluido No Existe Suficiente Elementos de Prueba','Asunto Totalmente Concluido No Existe Suficiente Elementos de Prueba'),('Caducidad de Procedimiento','Caducidad de Procedimiento'),('Causada Ejecutoria','Causada Ejecutoria'),('Cierre de Comite','Cierre de Comite'),('Dejar sin Efecto Legal','Dejar sin Efecto Legal')],string='MOTIVO DE CIERRE')
   #fin de agregar
    source_document_number = fields.Char('Source Document Number')
    origin_date = fields.Datetime('Origin Date', index=True)
    origin_complaint = fields.Char('Origin of the Complaint')
    employee_id = fields.Many2many('hr.employee', string='Employee')
    employee_id3 = fields.One2many('hr.base', 'id_name',string='Informacion Personal')

    actions = fields.Char('Actions')
    complainer = fields.One2many('hr.disiplinary.injured', 'id_expediente_injured', string='Parte de Quejas',
                                 help='Who makes the complaint')
    id_antecedente = fields.One2many('hr.disiplinary.precedent', 'id_expediente_precedent')
    image_medium = fields.Binary('Image', related='type_expedient_id.image', store=True)
    image_employee = fields.Binary('image_employee', related='employee_id.image_1920', store=True)
    color = fields.Integer()
    ##se  modifica  este  vista  para
    employee_name = fields.Char(related='employee_id.name', string="Employee Name")  # = nombre



    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # retrieve job_id from the context and write the domain: ids + contextual columns (job or default)
        type_expedient_id = self._context.get('default_type_expedient_id')
        search_domain = [('expedient_ids', '=', False)]
        if type_expedient_id:
            search_domain = ['|', ('expedient_ids', '=', type_expedient_id)] + search_domain
        if stages:
            search_domain = ['|', ('id', 'in', stages.ids)] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    # def reset_applicant(self):
    #     #     """ Reinsert the expedient into the  pipe in the first stage"""
    #     #     default_stage_id = self._default_stage_id()
    #     #     self.write({'active': True, 'stage_id': default_stage_id})


### solucionar este show ---1
class ExpedientDisciplinaryTaskType(models.Model):
    _name = 'expedient.disciplinary.task.type'
    _description = 'Task Stage Expedient'

    def _get_default_expedient_ids(self):
        default_expedient_id = self.env.context.get('default_expedient_id')
        return [default_expedient_id] if default_expedient_id else None

    name = fields.Char(string='Stage name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    expedient_id = fields.Many2many('hr.expedient.disiplinary', 'expedient_task_tipe_rel', 'type_id', 'expedient_id',
                                    string='expedient', default=_get_default_expedient_ids)

    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda s: _('Blocked'), translate=True, required=True,
        help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda s: _('Ready for Next Stage'), translate=True, required=True,
        help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda s: _('In Progress'), translate=True, required=True,
        help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')


# final de este  show

### solucionar este show ---2
class hr_expedient_disiplinary(models.Model):
    _name = 'hr.expedient.disiplinary'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Control de expedientes.'

    def expedient_view(self):
        self.ensure_one()
        domain = [
            ('id_expediente_injured', '=', self.id)]
        return {
            'name': _('Expedients'),
            'domain': domain,
            'res_model': 'hr.disiplinary.injured',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                              Click to Create for New Expedients
                           </p>'''),
            'limit': 80,
            'context': "{'default_id_expediente_injured': %s}" % self.id
        }

    # Informacion del Expediente
    folio = fields.Char('Folio de Expedinete', required=True)
    fecha_apertura = fields.Date('Fecha de Apertura', required=True)
    tipo_procedencia = fields.Selection([('interna', 'Interna'), ('externa', 'Externa')])
    procedencia_expediente = fields.Char('Procedencia del Expediente')
    # Datos de Informacion del Remitente.
    remitente = fields.Char('Persona Quien Firma')
    dependencia_remitente = fields.Char('Dependencia del Remitente')
    # Datos de origen del expediente
    no_Documento_o = fields.Char('No. Documento Origen')
    fecha_origen = fields.Date('Fecha')
    procendencia_denuncia = fields.Char('Procedencia de denuncia')
    # reverce_employee_id = fields.Many2one('hr.employee', string='Emplore_reverce')
    employee_id = fields.Many2many('hr.employee', string='Employee Inv')
    conducta = fields.Char('Conducta')
    observaciones = fields.Text('Observaciones')
    id_injured = fields.One2many('hr.disiplinary.injured', 'id_expediente_injured', 'Quejoso',
                                 help='Quien interpone la queja')
    id_antecedente = fields.One2many('hr.disiplinary.precedent', 'id_expediente_precedent')
    type_expedient_id = fields.Many2one('hr.type.exp.disiplinary', 'Tipo_Expediente')
    image_medium = fields.Binary('Image', related='type_expedient_id.image', store=True)
    image_employee = fields.Binary('image_employee', related='employee_id.image_1920', store=True)
    color = fields.Integer()
    type_ids = fields.Many2many('expedient.disciplinary.task.type', 'expedient_task_type_rel', 'expedient_id',
                                'type_id',
                                string='Expedient Stages')

# final de este  show

# parte del quejas
class hr_disiplinary_injured(models.Model):
    _name = 'hr.disiplinary.injured'
    _description = 'Tabla para registrar los  datos del agraviado o quejoso'

    def _get_default_expedient_ids(self):
        default_expedient_id = self.env.context.get('default_expedient_id')
        return [default_expedient_id] if default_expedient_id else None
    #una propuesta
    Name = fields.Char(string='NOMBRE COMPLETO')
    Domicilio= fields.Char(string="DOMICILIO")
    clv1 = fields.Boolean('No Conoce El Domicilio?', default=False)
    #fin de propuesta
    address = fields.Many2one('feature.location.district', string='Autocompletar Dirección',
                              ondelete='restrict')
    zip_address = fields.Char(related='address.zip_code', store=True, string='Código Postal')
    district_address = fields.Char(related='address.name', store=True)
    city_address = fields.Char(related='address.city_id.name', store=True, string='Ciudad')
    state_address = fields.Char(related='address.state_id.name', store=True, string='Estado')
    country_address = fields.Char(related='address.country_id.name', store=True, string='País')
    # LA sEGUNDA pArTe
    street = fields.Char(string='Calle principal')
    street2 = fields.Char(string='Calle 2')
    number_interior = fields.Char(string='Número Interior')
    number_exterior = fields.Char(string='Número Exterior')

    id_expediente_injured = fields.Many2one('hr.expedient', 'Id Expediente', default=_get_default_expedient_ids)
    name = fields.Char(related='id_expediente_injured.name', string='Id Expedinete')
    observaciones = fields.Text('Observaciones')


# prueba 22/08/2022 checar
class hr_base(models.Model):
    _name = 'hr.base'
    _inherit = "hr.expedient"
    _description = 'Inv'

    id_name = fields.Many2one('hr.expedient', string='Nombre')
    employee_id = fields.Many2one('hr.employee', string='Nombre_Completo')
    work_phone11 = fields.Char(related='employee_id.work_phone', store=True, string='Numero')
    mobile_phone11 = fields.Char(related='employee_id.mobile_phone', store=True, string='Email')
    department_id = fields.Many2one('hr.department', string='Departamento', related='employee_id.department_id')
    job_id = fields.Many2one('hr.job', string='Puesto de trabajo', related='employee_id.job_id')

    #una de propuesta
    clv = fields.Boolean('No Conoce El Numero de Empleado?', default=False)
    involocrados= fields.Char('INVOLUCRADOS')
    n_empleado=fields.Char('N-EMPLEADO')
    #fin de propuesta
    observaciones2 = fields.Text('Observaciones')
# fin de prueba 22/08/2022


## de antecedente---full
class hr_disiplinary_precedent(models.Model):
    _name = 'hr.disiplinary.precedent'
    _description = 'Tabla para capturar los antecednetes del expediente'

    # prueba
    # Direccion
    addres = fields.Many2one('feature.location.district', string='Autocompletar Dirección',
                             ondelete='restrict')
    zip_address = fields.Char(related='addres.zip_code', store=True, string='Código Postal')
    district_address = fields.Char(related='addres.name', store=True)
    city_address = fields.Char(related='addres.city_id.name', store=True, string='Ciudad')
    state_address = fields.Char(related='addres.state_id.name', store=True, string='Estado')
    country_address = fields.Char(related='addres.country_id.name', store=True, string='País')
    # LA sEGUNDA pArTe
    street = fields.Char(string='Calle principal')
    street2 = fields.Char(string='Calle 2')
    number_interior = fields.Char(string='Número Interior')
    number_exterior = fields.Char(string='Número Exterior')
    clv2 = fields.Boolean('No Conoce El Lugar Del Evento?', default=False)
    event_venue = fields.Char('LUGAR DEL EVENTO')
    #prouesta
    municipio_event= fields.Char('MUNICIPIO DEL EVENTO')
    #fin de porpuesta
    Date_Time = fields.Date('FECHA DEL EVENTO')
    id_expediente_precedent = fields.Many2one('hr.expedient', 'Id Expediente')
    name = fields.Char(related='id_expediente_precedent.name', string='Id Expedinete')
    observaciones1 = fields.Text('Observaciones')
