from distutils.log import error
from djongo import models
from django.db.models import DEFERRED

from djongo.models.fields import EmbeddedField,ArrayField
from django.core.exceptions import ValidationError

from django.db.models import DateTimeField,DateField,TimeField

from django.db.models.fields import NOT_PROVIDED

from django.utils import timezone
import typing

# override the model.EmbeddedField to achieve the skippable null field feature
class EmbeddedDocument(EmbeddedField): 
    
    def __init__(self,model_container, *args, **kwargs) -> None:
        self.model_container = model_container
        super().__init__(model_container = model_container,
                 model_form_class = None,
                 model_form_kwargs = None,
                 *args, **kwargs)

    def _save_value_thru_fields(self, func_name: str, value: dict, *other_args):
        # override the method to save the fields in db which does not have any null value
        processed_value = {}
        errors = {}
        # print(type(self.model_container._meta.get_fields()[3]))
        # print(self.model_container._meta.get_fields()[3].get_db_prep_value())

        print("this is field value : ",value)

        for field in self.model_container._meta.get_fields():
            try:
                field_value = None
                try:
                    field_value = value[field.attname]

                    if field_value is None or field_value =="":
                        # if field contains a "default value" then any null or blank values are not allowed.
                        if not isinstance(field.default,type):
                            if field.blank is False and field.null is False:
                                raise ValidationError(f'"{field}" has a default value as "{field.default}".It can\'t be changed to null or "" ')
                           
                        if field.blank is False or field.null is False:
                            # raise ValidationError(f'Value for field "{field}" not supported as it is not allowed empty values')
                            field_value = None
                            
                        # null values or "" or both  are allowed to the field, keep the value as it is. By defualt django model doesnot allow both to true
                        if field.null is True and field_value is None:
                            processed_value[field.attname] = getattr(field, func_name)(field_value, *other_args)
                        elif field.blank is True and field_value =="":
                            processed_value[field.attname] = getattr(field, func_name)(field_value, *other_args)
                        elif field.blank is True and field.null is True:
                            processed_value[field.attname] = getattr(field, func_name)(field_value, *other_args)
                        else:
                            raise ValidationError(f'Value for field "{field}" not supported as it is not allowed "{field_value}" values')
                        
                except KeyError:
                    # if no value is passed from the frontend and if field contain a default value the set it to default val
                    if field.blank is False and field.null is False:
                        if not isinstance(field.default,type): 
                            # having a default value and we didnot pass any value regarding this field
                            processed_value[field.attname] = getattr(field, func_name)(field.default, *other_args)
                        else :
                            # did not pass any value from frontend
                            field_value = None
                            

                    # setting DateTimeField or DateField value. It gets fired when user did't provide any value for these fields.
                        # auto_now_add - editable=False - fire at only iintial instance creation
                    if isinstance(field,DateTimeField) or isinstance(field,DateField) or isinstance(field,TimeField): 
                        current_time = timezone.now()
                        formatted_value = field.to_python(current_time)
                        if field.auto_now_add is True:
                            field.editable = False
                        elif field.auto_now is True:
                            field.editable = True
                        try :
                            field._check_fix_default_value()
                            processed_value[field.attname] = getattr(field, func_name)(formatted_value, *other_args)
                        except Warning as w:
                            errors[field.name] = w.with_traceback()

                # print(f'fields are called for "{field}" and defualt value for fields "{field.default}"')

                #  can not set the custom values for date and datetime fields if auto_now or auto now_add true.
                if (isinstance(field,DateTimeField) or isinstance(field,DateField) or isinstance(field,TimeField))\
                        and (field.auto_now is True or field.auto_now_add is True):
                    field_value = None

                if field_value is not None and not isinstance(field.default,NOT_PROVIDED) : 
                    print(f'fields are called for "{field}"') 
                    processed_value[field.attname] = getattr(field, func_name)(field_value, *other_args)


            except ValidationError as e:
                errors[field.name] = e.error_list

        if errors:
            e = ValidationError(errors)
            raise ValidationError(str(e))
 
        return processed_value 

    def _value_thru_fields(self, func_name: str, value: dict, *other_args):
        # override the method to fetch the fields from db which does not have any null value
        processed_value = {}
        for field in self.model_container._meta.get_fields():
            try:
                field_value = value[field.attname]
            except KeyError:
                continue
            if field_value is not None:
                processed_value[field.attname] = getattr(field, func_name)(field_value, *other_args)
        return processed_value

# override the model.ArrayField to achieve the skippable null field feature
class ArrayDocument(ArrayField):
    def __init__(self,model_container, *args, **kwargs) -> None:
        self.model_container = model_container
        super().__init__(model_container = model_container,
                 model_form_class = None,
                 model_form_kwargs = None,
                 *args, **kwargs)
    
    def _save_value_thru_fields(self, func_name: str, value: typing.Union[list, dict], *other_args):

        EmbeddedDocumentObj = EmbeddedDocument(model_container=self.model_container)
        processed_value = []
        for pre_dict in value:
            post_dict =EmbeddedDocumentObj._save_value_thru_fields(func_name,
                                                            pre_dict,
                                                            *other_args)
            processed_value.append(post_dict)
        return processed_value

# override the save method to achieve the non null constraints in base model
class Test(models.Model):
    _id = models.ObjectIdField()
    msg = models.CharField(max_length=200,blank = True, null = True)
    test = models.CharField(max_length=200,blank = True, null = True)
    count = models.IntegerField(blank=True,null=True)
    date_time_testing = models.DateTimeField(blank=True,null=True)
    required_fields = models .CharField(max_length = 50,blank=False,null = False,default="abc")

    
    class Meta: 
        db_table = "test" 
    
    @classmethod
    def from_db(cls, db, field_names, values):
        print("from db is called")
        if len(values) != len(cls._meta.concrete_fields):
            values_iter = iter(values)
            values = [
                next(values_iter) if f.attname in field_names else DEFERRED
                for f in cls._meta.concrete_fields
            ]
        new = cls(*values)
        new._state.adding = False
        new._state.db = db
        return new

    def save(self, *args, **kwargs): 
        # field optimization can be done by both _concrete_fields and local_concrete_fields 
        # print(self._state.adding)
        # print("\n")

        # fetching non-pk fields 
        non_pks = [f for f in self._meta.local_concrete_fields if not f.primary_key]
        # print(non_pks)
        # get the values of the fields 
        raw= True
        values = [(f, None, (getattr(self, f.attname) if raw else f.pre_save(self, False)))
                      for f in non_pks]
        # print(values)

        non_null_values_fields = []
        for f in non_pks:
            field_value = getattr(self,f.attname)
            if field_value is not None and field_value != "":
                print(field_value)
                non_null_values_fields.append(f)
        
        non_null_values_fields = tuple(non_null_values_fields)
        self._meta.local_concrete_fields = non_null_values_fields



        # print(self._meta.concrete_fields)
        # concrete_fields_list = list(self._meta.local_concrete_fields)
        # concrete_fields_list.pop()
        # self._meta.local_concrete_fields = tuple(concrete_fields_list)
        # print("save is called========")
        # print(self._meta.concrete_fields)

        # print( self._meta.local_concrete_fields)
        # if not self._state.adding and (
        #         self.msg != self._loaded_values['creator_id']):
        #     raise ValueError("Updating the value of creator isn't allowed")
        
        super().save(*args, **kwargs)


class TestAbs(models.Model):
    desc = models.CharField(max_length=30,blank=True,null=True)
    desc1 = models.CharField(max_length=30,blank=False,null=False,default = "default values")
    desc2 = models.CharField()

    # file_testing_fields = models.FileField(upload_to='/static/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_at_date = models.DateField(auto_now_add=True)
    updated_at_date = models.DateField(auto_now=True)
    
    created_at_time = models.TimeField(auto_now_add=True)
    updated_at_time = models.TimeField(auto_now=True)

    class Meta:
        abstract = True 
 
class TestEmbed(models.Model):
    _id = models.ObjectIdField()
    test_embed = EmbeddedDocument(model_container=TestAbs)
    test_array = ArrayDocument(model_container=TestAbs)

    class Meta:
        db_table = "TestEmbed"
    def save(self, *args, **kwargs): 
            # field optimization can be done by both _concrete_fields and local_concrete_fields  
            non_pks = [f for f in self._meta.local_concrete_fields if not f.primary_key] 
            raw= True
            values = [(f, None, (getattr(self, f.attname) if raw else f.pre_save(self, False)))
                        for f in non_pks]  
            non_null_values_fields = [] 
            try:
                for f in non_pks:
                    field_value = getattr(self,f.attname)
                    if field_value is not None and field_value != "": 
                        non_null_values_fields.append(f)
                
                non_null_values_fields = tuple(non_null_values_fields)
                self._meta.local_concrete_fields = non_null_values_fields 
            except :
                pass
            
            super().save(*args, **kwargs)


# save()-->save_base()-->_save_table(){local_concrete_fields}