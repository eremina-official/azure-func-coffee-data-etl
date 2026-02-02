from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
import json


class ProductParameter(BaseModel):
    id: Optional[str] = None
    valuesIds: Optional[list] = None
    valuesLabels: Optional[list] = None
    values: Optional[list] = None
    name: Optional[str] = None
    unit: Optional[str] = None
    identifies_product: Optional[bool] = False


# Product class is used for raw data validation
# it can have optional helpers like converting data to json
# the logic how to fill missing values for DB insertion and
# the logic that describes how to loop & map parameters to a product should go to pipelines
class Product(BaseModel):
    id: str
    name: str
    category_id: Optional[str] = None
    publication_status: Optional[str] = None
    category: Dict
    description: Dict[str, Any] = Field(default_factory=dict)
    images: List[Dict[str, Any]] = Field(default_factory=list)
    ean: Optional[str] = None
    parameters: List

    # ---------- extract values from nested fields ----------
    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values):
        category = values.get("category")
        if category and "id" in category:
            values["category_id"] = category["id"]

        values["publication_status"] = values.get("publication", {}).get("status")
        return values

    # ---------- validators (Pydantic V2 style) ----------

    # @field_validator("name")
    # @classmethod
    # def name_not_empty(cls, v: str) -> str:
    #     if not v.strip():
    #         raise ValueError("Product name cannot be empty")
    #     return v

    # @field_validator("parameters", mode="before")
    # @classmethod
    # def ensure_parameters_list(cls, v):
    #     # Ensure parameters is always a list
    #     return v or []

    # ---------- helper methods ----------

    # def coffee_parameters(self) -> List[ProductParameter]:
    #     """Return only parameters relevant for coffee analysis."""
    #     excluded = {"weight_netto", "shipping_weight"}
    #     return [p for p in self.parameters if p.parameter_id not in excluded]

    # ------------------- helper to extract EAN -------------------
    def extract_ean(self) -> Optional[str]:
        """
        Extract EAN (GTIN) from parameters.
        Returns the first available value or None.
        """
        for param in self.parameters:
            if param.get("name") == "EAN (GTIN)":
                # Try 'value' first, then fallback to 'valuesLabels' if present
                if param.get("values"):
                    return param.get("values")[0]
                # If value is missing, attempt valuesLabels list
                values_labels = getattr(param, "valuesLabels", None)
                if values_labels:
                    return values_labels[0]
        return None

    def description_json(self) -> str:
        """Return description as JSON string for DB insertion."""
        return json.dumps(self.description or {})

    def images_json(self) -> str:
        """Return list of image URLs as JSON string for DB insertion."""
        return json.dumps([img.get("url") for img in self.images or []])

    def to_db_dict(self) -> Dict[str, Any]:
        """Flatten product for DB insertion, including JSON fields."""
        return {
            "id": self.id,
            "name": self.name,
            "category_id": self.category_id,
            "publication_status": self.publication_status,
            "description": self.description_json(),
            "images": self.images_json(),
            "ean": self.extract_ean(),
            "parameters": self.parameters,
        }
