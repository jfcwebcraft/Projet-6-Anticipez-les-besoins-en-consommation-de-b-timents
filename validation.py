# Schéma de validation Pydantic pour les données d'entrée de l'API

from pydantic import BaseModel, Field, model_validator
from typing import Optional


# Liste des usages non résidentiels acceptés par le modèle
VALID_PROPERTY_TYPES = [
    "Small- and Mid-Sized Office",
    "Large Office",
    "Medical Office",
    "Office",
    "K-12 School",
    "University",
    "Retail Store",
    "Supermarket / Grocery Store",
    "Restaurant",
    "Warehouse",
    "Distribution Center",
    "Refrigerated Warehouse",
    "Self-Storage Facility",
    "Laboratory",
    "Hotel",
    "Hospital",
    "Worship Facility",
    "Mixed Use Property",
    "Other",
]


class BuildingInput(BaseModel):
    """Caractéristiques structurelles d'un bâtiment pour la prédiction."""

    primary_property_type: str = Field(
        ...,
        examples=["Large Office", "Hotel", "K-12 School"],
    )

    year_built: int = Field(
        ...,
        ge=1800,
        le=2016,
    )

    number_of_buildings: int = Field(
        default=1,
        ge=1,
        le=100,
    )

    number_of_floors: int = Field(
        ...,
        ge=1,
        le=200,
    )

    property_gfa_total: float = Field(
        ...,
        gt=0,
        le=5_000_000,
    )

    property_gfa_parking: float = Field(
        default=0.0,
        ge=0,
        le=5_000_000,
    )

    property_gfa_building: float = Field(
        ...,
        gt=0,
        le=5_000_000,
    )

    largest_property_use_type_gfa: float = Field(
        ...,
        gt=0,
        le=5_000_000,
    )

    second_largest_property_use_type_gfa: float = Field(
        default=0.0,
        ge=0,
        le=5_000_000,
    )

    @model_validator(mode="after")
    def validate_coherence(self):
        """Vérifications de cohérence physique des surfaces du bâtiment."""
        errors = []

        if self.property_gfa_building > self.property_gfa_total:
            errors.append(
                "property_gfa_building ne peut pas être supérieur à property_gfa_total."
            )

        if self.property_gfa_parking > self.property_gfa_total:
            errors.append(
                "property_gfa_parking ne peut pas être supérieur à property_gfa_total."
            )

        # Somme bâtiment + parking (avec tolérance de 10% pour les arrondis)
        sum_parts = self.property_gfa_building + self.property_gfa_parking
        if sum_parts > self.property_gfa_total * 1.1:
            errors.append(
                f"La somme bâtiment ({self.property_gfa_building}) + parking "
                f"({self.property_gfa_parking}) = {sum_parts} dépasse la surface "
                f"totale ({self.property_gfa_total}) de plus de 10%."
            )

        if self.largest_property_use_type_gfa > self.property_gfa_building * 1.05:
            errors.append(
                "largest_property_use_type_gfa ne peut pas être très supérieur "
                "à property_gfa_building."
            )

        sum_uses = (
            self.largest_property_use_type_gfa
            + self.second_largest_property_use_type_gfa
        )
        if sum_uses > self.property_gfa_building * 1.1:
            errors.append(
                "La somme des surfaces d'usage dépasse la surface du bâtiment."
            )

        if self.primary_property_type not in VALID_PROPERTY_TYPES:
            errors.append(
                f"primary_property_type '{self.primary_property_type}' non reconnu. "
                f"Valeurs acceptées : {VALID_PROPERTY_TYPES}"
            )

        if errors:
            raise ValueError(" | ".join(errors))

        return self


def validate_input(data: BuildingInput) -> None:
    # pydantic valide déjà à l'instanciation, mais on peut rajouter des checks ici
    pass
