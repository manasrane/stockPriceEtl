
  
    

  create  table "db"."dev"."weather_report__dbt_tmp"
  
  
    as
  
  (
    

select * from "db"."dev"."staging"
  );
  