"""CommandAddress completeness and address uniqueness."""



from p1_modbus.command_address import CommandAddress, UNVERIFIED_ADDRS





def _all_addrs() -> list[int]:

    return [

        v

        for name, v in vars(CommandAddress).items()

        if not name.startswith("_") and isinstance(v, int)

    ]





def test_command_address_unique() -> None:

    addrs = _all_addrs()

    assert len(addrs) == len(set(addrs))





def test_unverified_addrs_documented() -> None:

    assert CommandAddress.M39 in UNVERIFIED_ADDRS

    assert CommandAddress.M46 in UNVERIFIED_ADDRS





def test_core_addresses_present() -> None:

    assert CommandAddress.G6 == 0x0001

    assert CommandAddress.M405 == 0x0104

    assert CommandAddress.M600 == 0x0109





def test_m601_m602_not_defined() -> None:

    names = {n for n in dir(CommandAddress) if not n.startswith("_")}

    assert "M601" not in names

    assert "M602" not in names


