from djongo import models
from django.db.models import DEFERRED

from djongo.models.fields import EmbeddedField
from django.core.exceptions import ValidationError



# override the model.EmbeddedField to achive the non-null constraints
class CustomEmbeddedField(EmbeddedField): 
    
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
        for field in self.model_container._meta.get_fields():
            try:
                try:
                    field_value = value[field.attname]
                except KeyError:
                    raise ValidationError(f'Value for field "{field}" not supplied')
                if field_value is not None:
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
    desc1 = models.CharField(max_length=30,blank=True,null=True) 
    class Meta:
        abstract = True 
 
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