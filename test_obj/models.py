from djongo import models
from django.db.models import DEFERRED
from sqlalchemy import desc

from djongo.models.fields import EmbeddedField,ModelField,FormedField
from django.core.exceptions import ValidationError

class CustomEmbeddedField(FormedField): 
    
    def __init__(self,model_container, *args, **kwargs) -> None:
        self.model_container = model_container
        super().__init__(model_container = model_container,
                 model_form_class = None,
                 model_form_kwargs = None,
                 *args, **kwargs)

    def _save_value_thru_fields(self, func_name: str, value: dict, *other_args):
        processed_value = {}
        errors = {}
        for field in self.model_container._meta.get_fields():
            try:
                try:
                    field_value = value[field.attname]
                except KeyError:
                    raise ValidationError(f'Value for field "{field}" not supplied')
                print("Field vlaues--> {}",field_value)
                if field_value is not None or field_value!="":
                    processed_value[field.attname] = getattr(field, func_name)(field_value, *other_args)
            except ValidationError as e:
                errors[field.name] = e.error_list

        if errors:
            e = ValidationError(errors)
            raise ValidationError(str(e))

        # return processed_value
        # print(processed_value)
        del processed_value["desc1"]
        return super()._save_value_thru_fields(func_name, processed_value, *other_args)

class Test(models.Model):
    _id = models.ObjectIdField()
    msg = models.CharField(max_length=200,blank = True, null = True)
    test = models.CharField(max_length=200,blank = True, null = True)
    count = models.IntegerField(blank=True,null=True)

    class Meta: 
        db_table = "test" 
    
    @classmethod
    def from_db(cls, db, field_names, values):
        # if len(values) != len(cls._meta.concrete_fields):
        print("from_db is called")
        values = list(values)
        values.reverse()
        values = [
            values.pop() if f.attname in ['test','count'] else DEFERRED
            for f in cls._meta.concrete_fields
        ]
        instance = cls(*values)
        instance._state.adding = False
        instance._state.db = db
        instance._loaded_values = dict(zip(field_names,values))
        return instance

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
    desc1 = models.CharField(max_length=30,blank=True,null=True)

    
    
    class Meta:
        abstract = True
        
        

    
    # return the object as the updated one means, ifany field doest not contain any value don't include it.

     



class TestEmbed(models.Model):
    _id = models.ObjectIdField()
    test_embed = CustomEmbeddedField(model_container=TestAbs)

    class Meta:
        db_table = "TestEmbed"
    def save(self, *args, **kwargs): 
            # field optimization can be done by both _concrete_fields and local_concrete_fields  
            non_pks = [f for f in self._meta.local_concrete_fields if not f.primary_key] 
            raw= True
            values = [(f, None, (getattr(self, f.attname) if raw else f.pre_save(self, False)))
                        for f in non_pks]  
            non_null_values_fields = []
            # print(non_pks)
            try:
                for f in non_pks:
                    field_value = getattr(self,f.attname)
                    if field_value is not None and field_value != "":
                        # print(field_value)
                        non_null_values_fields.append(f)
                
                non_null_values_fields = tuple(non_null_values_fields)
                self._meta.local_concrete_fields = non_null_values_fields 
            except :
                pass
            
            super().save(*args, **kwargs)

# save()-->save_base()-->_save_table(){local_concrete_fields}