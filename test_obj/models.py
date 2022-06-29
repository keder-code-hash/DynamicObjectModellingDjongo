from djongo import models
from django.db.models import DEFERRED

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

    
# save()-->save_base()-->_save_table(){local_concrete_fields}